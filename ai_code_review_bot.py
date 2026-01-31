#!/usr/bin/env python3
"""
AI Code Review Bot - GitHub Action
Performs automated code reviews on Pull Requests using configurable LLM APIs
"""

import os
import sys
import json
import yaml
import requests
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class Severity(Enum):
    """Review finding severity levels"""
    CRITICAL = ("🔴", "Critical", 5)
    HIGH = ("🟠", "High", 4)
    MEDIUM = ("🟡", "Medium", 3)
    LOW = ("🔵", "Low", 2)
    NITPICK = ("⚪", "Nitpick", 1)

    def __init__(self, emoji, label, priority):
        self.emoji = emoji
        self.label = label
        self.priority = priority


@dataclass
class ReviewFinding:
    """Represents a single review finding"""
    severity: Severity
    category: str
    message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None


@dataclass
class ReviewConfig:
    """Configuration for the review bot"""
    languages: List[str]
    severity_threshold: str
    max_comments: int
    fail_on_severity: Optional[str]
    ignore_patterns: List[str]
    custom_prompt: Optional[str]
    review_tone: str
    focus_areas: List[str]


class LLMClient:
    """Generic LLM API client supporting multiple providers"""
    
    def __init__(self, provider: str, api_key: str, model: str, api_base: Optional[str] = None):
        self.provider = provider.lower()
        self.api_key = api_key
        self.model = model
        self.api_base = api_base or self._get_default_api_base()
        
    def _get_default_api_base(self) -> str:
        """Get default API base URL for known providers"""
        defaults = {
            'openai': 'https://api.openai.com/v1',
            'anthropic': 'https://api.anthropic.com/v1',
            'azure': os.getenv('AZURE_OPENAI_ENDPOINT', ''),
            'google': 'https://generativelanguage.googleapis.com/v1beta',
            'mistral': 'https://api.mistral.ai/v1',
            'groq': 'https://api.groq.com/openai/v1',
        }
        return defaults.get(self.provider, os.getenv('LLM_API_BASE', 'https://api.openai.com/v1'))
    
    def generate_review(self, prompt: str, max_tokens: int = 4000) -> str:
        """Generate review using the configured LLM"""
        if self.provider == 'anthropic':
            return self._call_anthropic(prompt, max_tokens)
        elif self.provider in ['openai', 'azure', 'groq', 'mistral']:
            return self._call_openai_compatible(prompt, max_tokens)
        elif self.provider == 'google':
            return self._call_google(prompt, max_tokens)
        else:
            return self._call_openai_compatible(prompt, max_tokens)
    
    def _call_anthropic(self, prompt: str, max_tokens: int) -> str:
        """Call Anthropic Claude API"""
        headers = {
            'x-api-key': self.api_key,
            'anthropic-version': '2023-06-01',
            'content-type': 'application/json'
        }
        
        data = {
            'model': self.model,
            'max_tokens': max_tokens,
            'messages': [
                {'role': 'user', 'content': prompt}
            ]
        }
        
        response = requests.post(
            f'{self.api_base}/messages',
            headers=headers,
            json=data,
            timeout=120
        )
        response.raise_for_status()
        return response.json()['content'][0]['text']
    
    def _call_openai_compatible(self, prompt: str, max_tokens: int) -> str:
        """Call OpenAI-compatible API (OpenAI, Azure, Groq, Mistral, etc.)"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        # Azure OpenAI uses api-key header instead
        if self.provider == 'azure':
            headers = {
                'api-key': self.api_key,
                'Content-Type': 'application/json'
            }
        
        data = {
            'model': self.model,
            'messages': [
                {'role': 'user', 'content': prompt}
            ],
            'max_tokens': max_tokens,
            'temperature': 0.3
        }
        
        response = requests.post(
            f'{self.api_base}/chat/completions',
            headers=headers,
            json=data,
            timeout=120
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    
    def _call_google(self, prompt: str, max_tokens: int) -> str:
        """Call Google Gemini API"""
        headers = {
            'Content-Type': 'application/json'
        }
        
        data = {
            'contents': [
                {'parts': [{'text': prompt}]}
            ],
            'generationConfig': {
                'maxOutputTokens': max_tokens,
                'temperature': 0.3
            }
        }
        
        response = requests.post(
            f'{self.api_base}/models/{self.model}:generateContent?key={self.api_key}',
            headers=headers,
            json=data,
            timeout=120
        )
        response.raise_for_status()
        return response.json()['candidates'][0]['content']['parts'][0]['text']


class GitHubClient:
    """GitHub API client for PR operations"""
    
    def __init__(self, token: str, repo: str, pr_number: int):
        self.token = token
        self.repo = repo
        self.pr_number = pr_number
        self.api_base = 'https://api.github.com'
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
    
    def get_pr_diff(self) -> str:
        """Get the full diff for the PR"""
        url = f'{self.api_base}/repos/{self.repo}/pulls/{self.pr_number}'
        headers = {**self.headers, 'Accept': 'application/vnd.github.v3.diff'}
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text
    
    def get_pr_files(self) -> List[Dict[str, Any]]:
        """Get list of changed files in the PR"""
        url = f'{self.api_base}/repos/{self.repo}/pulls/{self.pr_number}/files'
        
        response = requests.get(url, headers=self.headers, timeout=30)
        response.raise_for_status()
        return response.json()
    
    def get_file_content(self, file_path: str, ref: str = 'HEAD') -> Optional[str]:
        """Get content of a specific file"""
        url = f'{self.api_base}/repos/{self.repo}/contents/{file_path}'
        params = {'ref': ref}
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            import base64
            content = base64.b64decode(response.json()['content']).decode('utf-8')
            return content
        except Exception as e:
            print(f"Warning: Could not fetch {file_path}: {e}")
            return None
    
    def post_review_comment(self, body: str) -> None:
        """Post a review comment on the PR"""
        url = f'{self.api_base}/repos/{self.repo}/issues/{self.pr_number}/comments'
        
        data = {'body': body}
        response = requests.post(url, headers=self.headers, json=data, timeout=30)
        response.raise_for_status()
        print(f"✓ Posted review comment to PR #{self.pr_number}")


class CodeReviewBot:
    """Main code review bot orchestrator"""
    
    def __init__(self, config: ReviewConfig, llm_client: LLMClient, github_client: GitHubClient):
        self.config = config
        self.llm = llm_client
        self.github = github_client
    
    def run_review(self) -> None:
        """Execute the complete review process"""
        print("🤖 Starting AI Code Review Bot...")
        
        # 1. Fetch PR data
        print("📥 Fetching PR diff and files...")
        pr_diff = self.github.get_pr_diff()
        pr_files = self.github.get_pr_files()
        
        # 2. Filter files based on config
        filtered_files = self._filter_files(pr_files)
        print(f"📁 Analyzing {len(filtered_files)} files")
        
        if not filtered_files:
            print("ℹ️  No files to review after filtering")
            return
        
        # 3. Build context
        print("🔍 Building code context...")
        context = self._build_context(pr_diff, filtered_files)
        
        # 4. Generate review prompt
        print("📝 Generating review prompt...")
        prompt = self._build_review_prompt(context)
        
        # 5. Get AI review
        print("🧠 Analyzing code with AI...")
        review_text = self.llm.generate_review(prompt)
        
        # 6. Parse and format review
        print("📋 Formatting review...")
        formatted_review = self._format_review(review_text)
        
        # 7. Post to GitHub
        print("📤 Posting review to GitHub...")
        self.github.post_review_comment(formatted_review)
        
        # 8. Check severity threshold
        self._check_severity_threshold(review_text)
        
        print("✅ Review completed successfully!")
    
    def _filter_files(self, files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter files based on configuration"""
        filtered = []
        for file in files:
            filename = file['filename']
            
            # Check ignore patterns
            if any(self._matches_pattern(filename, pattern) for pattern in self.config.ignore_patterns):
                continue
            
            # Check language/extension
            if self.config.languages and not any(
                filename.endswith(f'.{lang}') for lang in self.config.languages
            ):
                continue
            
            filtered.append(file)
        
        return filtered
    
    def _matches_pattern(self, filename: str, pattern: str) -> bool:
        """Check if filename matches a pattern"""
        import fnmatch
        return fnmatch.fnmatch(filename, pattern)
    
    def _build_context(self, diff: str, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build context for the review"""
        context = {
            'diff': diff,
            'files': [],
            'summary': {
                'total_files': len(files),
                'additions': sum(f.get('additions', 0) for f in files),
                'deletions': sum(f.get('deletions', 0) for f in files),
            }
        }
        
        for file in files[:20]:  # Limit to prevent token overflow
            file_info = {
                'filename': file['filename'],
                'status': file['status'],
                'additions': file.get('additions', 0),
                'deletions': file.get('deletions', 0),
                'patch': file.get('patch', ''),
            }
            context['files'].append(file_info)
        
        return context
    
    def _build_review_prompt(self, context: Dict[str, Any]) -> str:
        """Build the prompt for LLM review"""
        base_prompt = f"""You are an expert code reviewer performing a thorough analysis of a Pull Request.

**Review Configuration:**
- Tone: {self.config.review_tone}
- Focus Areas: {', '.join(self.config.focus_areas)}
- Languages: {', '.join(self.config.languages) if self.config.languages else 'all'}

**PR Summary:**
- Files changed: {context['summary']['total_files']}
- Lines added: {context['summary']['additions']}
- Lines deleted: {context['summary']['deletions']}

**Your Task:**
Analyze the code changes and provide a structured review covering:

1. **Logical & Semantic Analysis**
   - Logic correctness and edge cases
   - API usage and patterns
   - Potential bugs or incorrect assumptions

2. **Code Quality & Standards**
   - Naming conventions and code style
   - Code organization and structure
   - Language-specific best practices

3. **Security & Performance**
   - Security vulnerabilities
   - Performance concerns
   - Resource management issues

**Output Format:**
Provide your review as structured JSON with this exact schema:

{{
  "summary": "Brief overall assessment (2-3 sentences)",
  "findings": [
    {{
      "severity": "CRITICAL|HIGH|MEDIUM|LOW|NITPICK",
      "category": "Logic|Security|Performance|Style|Best Practice",
      "message": "Clear, actionable description",
      "file": "filename (if applicable)",
      "line": line_number (if applicable, else null)
    }}
  ],
  "positive_notes": ["Things done well"],
  "overall_recommendation": "APPROVE|REQUEST_CHANGES|COMMENT"
}}

**Severity Guidelines:**
- CRITICAL: Security flaws, data loss, crashes
- HIGH: Logic bugs, incorrect behavior
- MEDIUM: Maintainability, reliability improvements
- LOW: Style improvements
- NITPICK: Optional polish

**Important:**
- Be concise and actionable
- Avoid generic statements
- Focus on {', '.join(self.config.focus_areas)} if specified
- Maximum {self.config.max_comments} findings

"""

        if self.config.custom_prompt:
            base_prompt += f"\n**Additional Instructions:**\n{self.config.custom_prompt}\n\n"
        
        # Add diff content
        base_prompt += "\n**Code Changes:**\n\n"
        
        for file_info in context['files']:
            base_prompt += f"\n### File: {file_info['filename']} ({file_info['status']})\n"
            if file_info['patch']:
                base_prompt += f"```diff\n{file_info['patch'][:2000]}\n```\n"  # Limit patch size
        
        base_prompt += "\n\nProvide your review now in the JSON format specified above."
        
        return base_prompt
    
    def _format_review(self, review_json: str) -> str:
        """Format the AI review into a GitHub comment"""
        try:
            # Extract JSON from potential markdown code blocks
            if '```json' in review_json:
                review_json = review_json.split('```json')[1].split('```')[0].strip()
            elif '```' in review_json:
                review_json = review_json.split('```')[1].split('```')[0].strip()
            
            review = json.loads(review_json)
        except json.JSONDecodeError as e:
            print(f"Warning: Could not parse JSON, using raw output. Error: {e}")
            return f"## 🤖 AI Code Review\n\n{review_json}"
        
        # Build formatted comment
        comment = "## 🤖 AI Code Review\n\n"
        comment += f"**Summary:** {review.get('summary', 'No summary provided')}\n\n"
        
        findings = review.get('findings', [])
        
        if not findings:
            comment += "✅ **No issues found!** The code looks good.\n\n"
        else:
            # Group by severity
            by_severity = {}
            for finding in findings:
                severity = finding.get('severity', 'MEDIUM')
                if severity not in by_severity:
                    by_severity[severity] = []
                by_severity[severity].append(finding)
            
            # Display in priority order
            for sev in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'NITPICK']:
                if sev in by_severity:
                    severity_enum = Severity[sev]
                    comment += f"### {severity_enum.emoji} {severity_enum.label} Issues\n\n"
                    
                    for finding in by_severity[sev]:
                        location = ""
                        if finding.get('file'):
                            location = f"**`{finding['file']}`**"
                            if finding.get('line'):
                                location += f" (line {finding['line']})"
                            location += ": "
                        
                        category = finding.get('category', 'General')
                        message = finding.get('message', 'No description')
                        comment += f"- {location}**[{category}]** {message}\n"
                    
                    comment += "\n"
        
        # Add positive notes if any
        positive = review.get('positive_notes', [])
        if positive:
            comment += "### ✨ Positive Highlights\n\n"
            for note in positive[:5]:
                comment += f"- {note}\n"
            comment += "\n"
        
        # Add recommendation
        recommendation = review.get('overall_recommendation', 'COMMENT')
        emoji_map = {
            'APPROVE': '✅',
            'REQUEST_CHANGES': '🔄',
            'COMMENT': '💬'
        }
        comment += f"{emoji_map.get(recommendation, '💬')} **Recommendation:** {recommendation}\n\n"
        comment += "---\n*Generated by AI Code Review Bot*"
        
        return comment
    
    def _check_severity_threshold(self, review_text: str) -> None:
        """Check if review contains findings above severity threshold"""
        if not self.config.fail_on_severity:
            return
        
        fail_severity = Severity[self.config.fail_on_severity]
        
        try:
            if '```json' in review_text:
                review_text = review_text.split('```json')[1].split('```')[0].strip()
            review = json.loads(review_text)
            
            for finding in review.get('findings', []):
                finding_severity = Severity[finding.get('severity', 'LOW')]
                if finding_severity.priority >= fail_severity.priority:
                    print(f"❌ Found {finding_severity.label} issue, failing build as configured")
                    sys.exit(1)
        except:
            pass


def load_config() -> ReviewConfig:
    """Load configuration from file or environment"""
    config_path = os.getenv('CONFIG_PATH', '.ai-review.yml')
    
    # Default configuration
    config = {
        'languages': [],
        'severity_threshold': 'MEDIUM',
        'max_comments': 20,
        'fail_on_severity': None,
        'ignore_patterns': ['*.md', '*.txt', '*.lock', 'package-lock.json'],
        'custom_prompt': None,
        'review_tone': 'professional',
        'focus_areas': ['logic', 'security', 'best-practices']
    }
    
    # Try to load from file
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                file_config = yaml.safe_load(f) or {}
                config.update(file_config)
                print(f"✓ Loaded configuration from {config_path}")
        except Exception as e:
            print(f"⚠ Warning: Could not load config file: {e}")
    
    # Environment variable overrides
    if os.getenv('LANGUAGES'):
        config['languages'] = os.getenv('LANGUAGES').split(',')
    if os.getenv('MAX_COMMENTS'):
        config['max_comments'] = int(os.getenv('MAX_COMMENTS'))
    if os.getenv('FAIL_ON_SEVERITY'):
        config['fail_on_severity'] = os.getenv('FAIL_ON_SEVERITY')
    if os.getenv('REVIEW_TONE'):
        config['review_tone'] = os.getenv('REVIEW_TONE')
    if os.getenv('CUSTOM_PROMPT'):
        config['custom_prompt'] = os.getenv('CUSTOM_PROMPT')
    
    return ReviewConfig(**config)


def main():
    """Main entry point"""
    # Required environment variables
    github_token = os.getenv('GITHUB_TOKEN')
    repo = os.getenv('GITHUB_REPOSITORY')
    pr_number = os.getenv('PR_NUMBER')
    
    llm_provider = os.getenv('LLM_PROVIDER', 'openai')
    llm_api_key = os.getenv('LLM_API_KEY')
    llm_model = os.getenv('LLM_MODEL', 'gpt-4')
    llm_api_base = os.getenv('LLM_API_BASE')
    
    # Validate required variables
    if not all([github_token, repo, pr_number, llm_api_key]):
        print("❌ Error: Missing required environment variables")
        print("Required: GITHUB_TOKEN, GITHUB_REPOSITORY, PR_NUMBER, LLM_API_KEY")
        sys.exit(1)
    
    try:
        pr_number = int(pr_number)
    except ValueError:
        print(f"❌ Error: Invalid PR_NUMBER: {pr_number}")
        sys.exit(1)
    
    # Initialize components
    config = load_config()
    llm_client = LLMClient(llm_provider, llm_api_key, llm_model, llm_api_base)
    github_client = GitHubClient(github_token, repo, pr_number)
    
    # Run review
    bot = CodeReviewBot(config, llm_client, github_client)
    
    try:
        bot.run_review()
    except Exception as e:
        print(f"❌ Error during review: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()