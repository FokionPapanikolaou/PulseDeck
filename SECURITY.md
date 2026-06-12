# Security Policy

## Supported versions
Only the latest release of PulseDeck (currently **v2.5**) receives security
fixes. If you're on an older version, please update first via the
[Microsoft Store](https://apps.microsoft.com/detail/9P128R4SVXLC) or the
latest [GitHub release](https://github.com/FokionPapanikolaou/PulseDeck/releases/latest).

## Reporting a vulnerability

**Please do not open a public issue for security problems.**

Instead, use GitHub's private reporting:

β΅οΈ **[Report a vulnerability privately](https://github.com/FokionPapanikolaou/PulseDeck/security/advisories/new)**

I'll acknowledge within 72 hours and aim to ship a fix in the next release.
Coordinated disclosure is appreciated.

## What's in scope

PulseDeck is a small desktop utility β€” the realistic attack surface is:

- The optional weather widget making HTTPS calls to `ipapi.co` and
  `open-meteo.com`
- The optional auto-update check hitting `api.github.com`
- Reading Windows performance counters (PDH) and a few read-only registry
  keys
- The settings file (`config.json`)

If you find a way to make any of those misbehave (parsing crashes, traffic
redirection, privilege escalation, code execution from a crafted update
response, etc.), I'd like to hear about it.

## What's *not* in scope

- Microsoft Windows or the .NET runtime itself
- Third-party themes / hacks people apply on top of PulseDeck
- The Microsoft Store binary signing process (managed by Microsoft)

Thanks for helping keep PulseDeck safe! π›΅οΈ
