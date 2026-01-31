# AI Code Review Bot - GitHub Action

🤖 Automated, intelligent code review for your Pull Requests using any LLM provider (OpenAI, Anthropic Claude, Google Gemini, Azure, Mistral, Groq, or custom APIs).

## Features

✅ **Multi-LLM Support** - Works with OpenAI, Anthropic, Google, Azure, Mistral, Groq, and custom APIs  
✅ **Configurable Reviews** - Customize tone, focus areas, and severity thresholds  
✅ **Language Agnostic** - Supports Python, JavaScript, TypeScript, Go, Java, Rust, and more  
✅ **Security Focused** - Identifies vulnerabilities, injection risks, and security issues  
✅ **Smart Analysis** - Logic bugs, edge cases, performance issues, and best practices  
✅ **Severity Classification** - Critical, High, Medium, Low, and Nitpick categorization  
✅ **Zero Configuration** - Works out of the box with sensible defaults  

---

## Quick Start

### 1. Add to Your Repository

Create `.github/workflows/ai-review.yml`:

```yaml
name: AI Code Review

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  ai-review:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: AI Code Review
        uses: your-username/ai-code-review-action@v1
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          llm_api_key: ${{ secrets.OPENAI_API_KEY }}
          llm_provider: 'openai'
          llm_model: 'gpt-4'
```

### 2. Configure Secrets

Go to your repository **Settings → Secrets and variables → Actions** and add:

- `OPENAI_API_KEY` - Your OpenAI API key (or equivalent for other providers)

### 3. (Optional) Add Configuration File

Create `.ai-review.yml` in your repository root:

```yaml
languages:
  - py
  - js
  - ts

review_tone: professional

focus_areas:
  - security
  - logic
  - best-practices

max_comments: 15

ignore_patterns:
  - "*.md"
  - "dist/*"
```

---

## Deployment Guide

### Method 1: Deploy as a Public GitHub Action

1. **Create a new GitHub repository** for your action:
   ```bash
   mkdir ai-code-review-action
   cd ai-code-review-action
   git init
   ```

2. **Copy the action files**:
   - `ai_code_review_bot.py` → Root directory
   - `action.yml` → Root directory
   - `README.md` → Root directory
   - `.ai-review.yml` → Root directory (as example)

3. **Create the file structure**:
   ```
   ai-code-review-action/
   ├── action.yml
   ├── ai_code_review_bot.py
   ├── README.md
   └── .ai-review.yml (example)
   ```

4. **Commit and push**:
   ```bash
   git add .
   git commit -m "Initial AI Code Review Action"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/ai-code-review-action.git
   git push -u origin main
   ```

5. **Create a release**:
   - Go to your repository on GitHub
   - Click "Releases" → "Create a new release"
   - Tag: `v1` or `v1.0.0`
   - Title: "v1.0.0 - Initial Release"
   - Publish release

6. **Use in any repository**:
   ```yaml
   - uses: YOUR-USERNAME/ai-code-review-action@v1
     with:
       github_token: ${{ secrets.GITHUB_TOKEN }}
       llm_api_key: ${{ secrets.OPENAI_API_KEY }}
   ```

### Method 2: Use as a Local Action (Single Repository)

1. **Create action directory** in your repository:
   ```bash
   mkdir -p .github/actions/ai-review
   ```

2. **Copy files** to `.github/actions/ai-review/`:
   - `ai_code_review_bot.py`
   - `action.yml`

3. **Reference locally** in your workflow:
   ```yaml
   - uses: ./.github/actions/ai-review
     with:
       github_token: ${{ secrets.GITHUB_TOKEN }}
       llm_api_key: ${{ secrets.OPENAI_API_KEY }}
   ```

### Method 3: Deploy to GitHub Marketplace

1. Follow **Method 1** to create a public repository
2. Add these files to your repository:
   - `LICENSE` (required)
   - Good README with examples
   - `CONTRIBUTING.md` (recommended)

3. In `action.yml`, ensure branding is set:
   ```yaml
   branding:
     icon: 'check-circle'
     color: 'blue'
   ```

4. Create a release (v1.0.0)

5. Go to your repository → "Releases" → Click on your release → "Draft a new release"

6. Check "Publish this Action to the GitHub Marketplace"

7. Follow the marketplace guidelines and submit

---

## Testing Guide

### Test 1: Local Testing (Without GitHub)

Create a test script:

```python
# test_local.py
import os
os.environ['GITHUB_TOKEN'] = 'your-test-token'
os.environ['GITHUB_REPOSITORY'] = 'owner/repo'
os.environ['PR_NUMBER'] = '1'
os.environ['LLM_PROVIDER'] = 'openai'
os.environ['LLM_API_KEY'] = 'your-api-key'
os.environ['LLM_MODEL'] = 'gpt-3.5-turbo'

# Mock GitHub responses for testing
import ai_code_review_bot
# Run main function
ai_code_review_bot.main()
```

### Test 2: Test in a Fork

1. **Fork a public repository** with Python/JS code
2. **Add the action** to `.github/workflows/ai-review.yml`
3. **Configure secrets** in your fork
4. **Create a test PR** with some code changes
5. **Verify** the bot comments on the PR

### Test 3: Create a Test Repository

1. **Create a new repository** called `ai-review-test`

2. **Add sample code** with intentional issues:
   ```python
   # bad_code.py
   def process_user_input(user_input):
       # Security issue: SQL injection vulnerability
       query = "SELECT * FROM users WHERE name = '" + user_input + "'"
       
       # Logic issue: no error handling
       result = execute_query(query)
       
       # Performance issue: inefficient loop
       for i in range(len(result)):
           print(result[i])
   ```

3. **Add the workflow** file

4. **Create a PR** changing this file

5. **Verify** the AI bot identifies:
   - Security: SQL injection risk
   - Logic: Missing error handling
   - Performance: Inefficient iteration

### Test 4: Test Different LLM Providers

Test with each provider:

```yaml
# Test OpenAI
- uses: your-action@v1
  with:
    llm_provider: 'openai'
    llm_api_key: ${{ secrets.OPENAI_API_KEY }}
    llm_model: 'gpt-4'

# Test Anthropic Claude
- uses: your-action@v1
  with:
    llm_provider: 'anthropic'
    llm_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
    llm_model: 'claude-3-5-sonnet-20241022'

# Test Google Gemini
- uses: your-action@v1
  with:
    llm_provider: 'google'
    llm_api_key: ${{ secrets.GOOGLE_API_KEY }}
    llm_model: 'gemini-pro'

# Test Groq
- uses: your-action@v1
  with:
    llm_provider: 'groq'
    llm_api_key: ${{ secrets.GROQ_API_KEY }}
    llm_model: 'mixtral-8x7b-32768'
```

---

## Configuration Reference

### Workflow Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `github_token` | GitHub token for API access | Yes | - |
| `llm_provider` | LLM provider name | No | `openai` |
| `llm_api_key` | API key for LLM | Yes | - |
| `llm_model` | Model name | No | `gpt-4` |
| `llm_api_base` | Custom API endpoint | No | - |
| `languages` | File extensions to review (comma-separated) | No | All |
| `max_comments` | Maximum review findings | No | `20` |
| `fail_on_severity` | Fail if severity found | No | - |
| `review_tone` | Tone of review | No | `professional` |
| `custom_prompt` | Additional instructions | No | - |
| `config_path` | Path to config file | No | `.ai-review.yml` |

### Configuration File (.ai-review.yml)

```yaml
# Languages to review
languages:
  - py
  - js
  - ts
  - go

# Maximum findings to report
max_comments: 20

# Fail action on severity
fail_on_severity: CRITICAL  # or null

# Ignore patterns
ignore_patterns:
  - "*.md"
  - "dist/*"
  - "node_modules/*"

# Custom instructions
custom_prompt: |
  Focus on security and performance.
  Be strict about error handling.

# Review style
review_tone: professional  # professional, strict, mentoring, friendly

# Focus areas
focus_areas:
  - logic
  - security
  - performance
  - best-practices
```

---

## Supported LLM Providers

### OpenAI
```yaml
llm_provider: 'openai'
llm_model: 'gpt-4'  # or gpt-3.5-turbo, gpt-4-turbo
llm_api_key: ${{ secrets.OPENAI_API_KEY }}
```

### Anthropic Claude
```yaml
llm_provider: 'anthropic'
llm_model: 'claude-3-5-sonnet-20241022'
llm_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
```

### Google Gemini
```yaml
llm_provider: 'google'
llm_model: 'gemini-pro'
llm_api_key: ${{ secrets.GOOGLE_API_KEY }}
```

### Azure OpenAI
```yaml
llm_provider: 'azure'
llm_model: 'your-deployment-name'
llm_api_key: ${{ secrets.AZURE_OPENAI_KEY }}
llm_api_base: 'https://your-resource.openai.azure.com'
```
Also set: `AZURE_OPENAI_ENDPOINT` environment variable

### Mistral AI
```yaml
llm_provider: 'mistral'
llm_model: 'mistral-large-latest'
llm_api_key: ${{ secrets.MISTRAL_API_KEY }}
```

### Groq
```yaml
llm_provider: 'groq'
llm_model: 'mixtral-8x7b-32768'
llm_api_key: ${{ secrets.GROQ_API_KEY }}
```

### Custom / Self-Hosted
```yaml
llm_provider: 'openai'  # Use OpenAI-compatible format
llm_api_base: 'http://your-server:8000/v1'
llm_api_key: ${{ secrets.CUSTOM_API_KEY }}
llm_model: 'your-model-name'
```

---

## Advanced Examples

### Example 1: Security-Focused Review

```yaml
- uses: your-action@v1
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    llm_api_key: ${{ secrets.OPENAI_API_KEY }}
    review_tone: 'strict'
    fail_on_severity: 'HIGH'
    custom_prompt: |
      Focus heavily on security vulnerabilities:
      - SQL injection, XSS, CSRF
      - Authentication and authorization
      - Data validation and sanitization
      - Secure cryptography usage
```

### Example 2: Mentoring Mode for Junior Developers

```yaml
- uses: your-action@v1
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    llm_api_key: ${{ secrets.OPENAI_API_KEY }}
    review_tone: 'mentoring'
    custom_prompt: |
      Provide educational feedback for junior developers.
      Explain WHY something is an issue and HOW to fix it.
      Include links to documentation when relevant.
```

### Example 3: Performance-Critical Applications

```yaml
- uses: your-action@v1
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    llm_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
    llm_provider: 'anthropic'
    llm_model: 'claude-3-5-sonnet-20241022'
    custom_prompt: |
      This is a high-performance trading system.
      Prioritize:
      - Algorithm complexity (O(n) analysis)
      - Memory allocations
      - Lock contention
      - Cache efficiency
```

### Example 4: Multiple Languages

```yaml
- uses: your-action@v1
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    llm_api_key: ${{ secrets.OPENAI_API_KEY }}
    languages: 'py,js,ts,go,rs'
    custom_prompt: |
      Apply language-specific best practices:
      - Python: PEP 8, type hints
      - JavaScript/TypeScript: ESLint rules
      - Go: Effective Go guidelines
      - Rust: Clippy recommendations
```

---

## Troubleshooting

### Issue: "No review posted"
**Solution:** Check that:
1. PR has actual code changes (not just markdown)
2. Files match the `languages` filter
3. Files aren't in `ignore_patterns`
4. GitHub token has `pull-requests: write` permission

### Issue: "API rate limit exceeded"
**Solution:** 
- Use a more efficient model (gpt-3.5-turbo instead of gpt-4)
- Reduce `max_comments`
- Increase `languages` filter to review fewer files

### Issue: "Review is too generic"
**Solution:**
- Add specific `custom_prompt` instructions
- Use a more capable model (gpt-4, claude-3-5-sonnet)
- Provide context in `.ai-review.yml`

### Issue: "Token limit exceeded"
**Solution:**
- Large PRs may exceed token limits
- Configure `ignore_patterns` to skip generated files
- Split large PRs into smaller ones

### Issue: "Wrong LLM provider format"
**Solution:**
- Check provider-specific authentication
- Verify `llm_api_base` for custom endpoints
- Review model name format for your provider

---

## Cost Considerations

Approximate costs per review (varies by PR size):

| Provider | Model | Cost/Review | Notes |
|----------|-------|-------------|-------|
| OpenAI | gpt-3.5-turbo | $0.01-0.05 | Fast, economical |
| OpenAI | gpt-4 | $0.10-0.50 | Best quality |
| Anthropic | claude-3-5-sonnet | $0.05-0.30 | Great balance |
| Google | gemini-pro | $0.01-0.05 | Cost effective |
| Groq | mixtral-8x7b | $0.00-0.01 | Very fast, cheap |

**Tips to reduce costs:**
- Use cheaper models for simple PRs
- Filter by file type
- Set `max_comments` limit
- Ignore generated/vendor files

---

## Security Best Practices

1. **Never commit API keys** - Always use GitHub Secrets
2. **Use least-privilege tokens** - Only grant required permissions
3. **Review provider privacy** - Understand where your code is sent
4. **Use private repos carefully** - Ensure your LLM provider's terms allow it
5. **Rotate keys regularly** - Update API keys periodically

---

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

---

## License

MIT License - See LICENSE file for details

---

## Support

- 🐛 **Bug Reports**: Open an issue
- 💡 **Feature Requests**: Open an issue with "enhancement" label
- 📖 **Documentation**: Check the wiki
- 💬 **Questions**: Use GitHub Discussions

---

## Roadmap

- [ ] Inline PR comments (file/line specific)
- [ ] Auto-fix suggestions
- [ ] Learning from accepted/rejected suggestions
- [ ] IDE integration
- [ ] Custom rule packs per language
- [ ] Organization-wide shared prompts
- [ ] Review history and analytics

---

**Made with ❤️ for developers who want AI-powered code reviews**
