メモ管理用スクリプト

# usage
## 準備
- 依存ライブラリのインストール
```bash
pip install -r requirements.txt
```
- Confluence の personal access token(PAT)の準備
  - [このページ](https://confluence.atlassian.com/enterprise/using-personal-access-tokens-1026032365.html)を読んでPATを準備する
  - PATを./secrets/confluence_pat にテキストファイルで置く
- markdownを書く
  - markdownにはfront-matter形式でメタデータを含める
  ```markdown
  ---
  ancestor_id: ${親ページのid}
  base_url: https://${コンフルのドメイン}
  space_key: ${メモを置くスペースのキー}
  title: ${メモの名前}
  ---

  # ほげほげ
  ふがふが
  ```
## Confluence(server)へのアップロード
```bash
python ./upload_to_confluence.py ${markdownファイルへのパス} ${PATへのパス}
```