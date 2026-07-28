# Research: design-craft-absorption from ui-skills

## Upstream

- repo: https://github.com/ibelick/ui-skills
- mirror: `/Users/apple/Developer/Personal/oss-sync/design/skills/ui-skills`
- imported via manage-oss-sync into `design/skills`

## Why these four

| upstream | why absorb | why not whole registry |
|----------|------------|------------------------|
| baseline-ui | 直接解决 AI UI slop | registry 含大量风格/框架特化噪声 |
| fixing-accessibility | 产品交付刚需 | 可先做 critical 规则子集 |
| fixing-motion-performance | 动效性能是常见假漂亮 | 不必引入全部动画生态 skill |
| improve-ui | 只读审计+计划，契合 Beacon harness 边界 | 方法论强，适合 support-only |

## Explicit non-absorb (defer)

- fixing-metadata / SEO
- 185 registry remote skills
- ui-skills website/cli runtime as hard dependency

## Beacon fit

ui-skills = craft toolbox  
beacon-design = governed design harness  

Absorption pattern: **toolbox into harness support refs**, not harness replacement.
