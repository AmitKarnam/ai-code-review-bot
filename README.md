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
        uses: AmitKarnam/ai-code-review-bot@v0.0.1
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

### Test Different LLM Providers

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
