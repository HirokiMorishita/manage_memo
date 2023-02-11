メモ管理用スクリプト

# usage
## 準備
- 依存ライブラリのインストール
```bash
pip install -r requirements.txt
```
- Confluence の personal access token(PAT)の準備
  - [このページ](https://confluence.atlassian.com/enterprise/using-personal-access-tokens-1026032365.html)を読んでPATを準備する
## Confluence(server)へのアップロード
```bash
python ./upload_to_confluence.py ${markdownファイルへのパス} ${PATへのパス}
```