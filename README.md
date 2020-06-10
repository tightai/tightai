# Tight.ai SDK
> Serverless Model Hosting & Model Marketplace


## Install

`pip install tightai`

## Getting Started

### Sign up
- Go to [https://www.tight.ai/signup](https://www.tight.ai/signup)

## Authenticate
### Via Login

This will prompt you for your username (or email) and password you used to sign up on tight.ai. Your local system will store unique credentials (never your account password) so your machine can re-access your account at anytime.

_Python Shell_
```python
from tightai.auth import login
login()
```

_Command Line_ 

```
$ tight login
```

### Via Token
Tokens are simple to create and very useful when needing to authenticate in a different way.

> Coming soon.
