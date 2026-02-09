# 使用 GitHub Secrets 管理密钥

## 1. 在仓库里添加 Secret

1. 打开仓库 **Settings** → **Secrets and variables** → **Actions**
2. 点击 **New repository secret**
3. 按下面名称添加（与 `.env` 对应，便于在 Actions 里生成 `.env` 或注入环境变量）：

| Name        | 说明     |
|------------|----------|
| `ENV`      | 环境，如 prod |
| `DB_DSN`   | 数据库连接串 |
| `REDIS_DSN`| Redis 连接串 |
| `SECRET_KEY` | 应用密钥 |

如需在 CI 里构建/推送镜像，还可加：

| Name           | 说明           |
|----------------|----------------|
| `DOCKERHUB_USERNAME` | Docker Hub 用户名 |
| `DOCKERHUB_TOKEN`    | Docker Hub 令牌   |

## 2. 在 workflow 里使用

- 通过 **env** 注入到 job/step，例如：
  ```yaml
  env:
    ENV: ${{ secrets.ENV }}
    DB_DSN: ${{ secrets.DB_DSN }}
    REDIS_DSN: ${{ secrets.REDIS_DSN }}
    SECRET_KEY: ${{ secrets.SECRET_KEY }}
  ```
- 或在某一步里写入 `.env` 再给 Docker Compose 用（见下方示例）。

## 3. 注意

- Secret 只在 workflow 运行时注入，**不要**在代码或 compose 文件里写真实密钥。
- 生产环境可建 **Environment**（如 `production`），在 Environment 里配置同名 Secret，优先级高于仓库级 Secret。
