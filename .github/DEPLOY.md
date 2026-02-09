# 如何运行与自动部署

## 一、先配置 Secrets

在仓库 **Settings → Secrets and variables → Actions** 里添加：

| Secret 名称   | 必填 | 说明 |
|---------------|------|------|
| `ENV`         | 是   | 如 `prod` |
| `DB_DSN`      | 是   | 数据库连接串 |
| `REDIS_DSN`   | 是   | Redis 连接串 |
| `SECRET_KEY`  | 是   | 应用密钥 |
| `SSH_HOST`    | 否*  | 部署目标机 IP 或域名（用 SSH 部署时必填） |
| `SSH_USER`    | 否*  | SSH 登录用户（用 SSH 部署时必填） |
| `SSH_PRIVATE_KEY` | 否* | SSH 私钥全文（用 SSH 部署时必填） |

\* 若用自托管 runner 在服务器上直接跑，可不配 SSH 相关，在 workflow 里改成直接执行 `docker compose`。

---

## 二、怎么运行

### 1. 手动运行

1. 打开仓库 **Actions** 页
2. 左侧选 **Deploy with secrets**
3. 点 **Run workflow** → 选分支（如 main）→ 再点 **Run workflow**
4. 等跑完看该次 run 的日志

### 2. 自动部署（推 main 即部署）

当前 workflow 已配置：**推送到 `main` 分支时会自动跑一次**。

- 不需要自动部署：在 `.github/workflows/example-use-secrets.yml` 里删掉整段：
  ```yaml
  push:
    branches: [main]
  ```
- 想改成别的分支（如 `release`）才部署：把 `branches: [main]` 改成 `branches: [release]`。

---

## 三、真正执行部署的两种方式

workflow 里会先用 Secrets 生成 `.env`，**部署**在 **Deploy** 这一步里完成，有两种常见做法：

### 方式 A：自托管 Runner 在服务器上

1. 在要部署的机器上安装并注册 [GitHub Actions self-hosted runner](https://docs.github.com/en/actions/hosting-your-own-runners)
2. 在 workflow 里把 `runs-on: ubuntu-latest` 改成你的 runner 的 label，例如 `runs-on: self-hosted`
3. 在 **Deploy** step 里直接写：
   ```yaml
   run: docker compose -f docker-compose.prod.yml --env-file .env up -d --build
   ```
4. 不需要配置 `SSH_*` 类 Secret

### 方式 B：用 GitHub 官方 Runner + SSH 到服务器

1. 在 Secrets 里配好 `SSH_HOST`、`SSH_USER`、`SSH_PRIVATE_KEY`
2. 在 **Deploy** step 里取消注释并保留那三行（写 key、scp、ssh 执行 docker compose）
3. 确保服务器上已安装 Docker、docker compose，且 SSH 用户有权限执行
4. 首次可先手动跑一次 workflow，看日志是否 scp/ssh 成功

---

## 四、小结

| 需求           | 操作 |
|----------------|------|
| 只手动部署     | 用 Actions → Deploy with secrets → Run workflow；不需要可删 `push` 触发 |
| 推 main 自动部署 | 保留 `push: branches: [main]`，推 main 即触发 |
| 部署到哪       | 在 **Deploy** step 里写：自托管 runner 上直接 `docker compose`，或 SSH 到服务器再执行 |
