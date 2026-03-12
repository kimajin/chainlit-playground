"""
Chainlit Step デモ：Claude風のツール表示UIを再現する

「ウェブを検索しました」のような折りたたみ式ステップ表示を
cl.Step を使って実装するサンプルです。
"""

import asyncio
import chainlit as cl

# ──────────────────────────────────────────────
# モック検索データ（実際はAPIを叩く部分）
# ──────────────────────────────────────────────

MOCK_SEARCH_DB: dict[str, list[dict]] = {
    "softbank openai": [
        {
            "title": "ソフトバンクグループとOpenAIによる合弁会社「SB OAI Japan」が発足",
            "url": "https://www.softbank.jp/corp/news/press/sbkk/2024/",
            "domain": "www.softbank.jp",
        },
        {
            "title": "SoftBank has fully funded $40B investment in OpenAI",
            "url": "https://www.cnbc.com/softbank-openai-investment",
            "domain": "www.cnbc.com",
        },
        {
            "title": "Completion of Additional $22.5 Billion Investment in OpenAI | SoftBank Group Corp.",
            "url": "https://group.softbank/news/2024/",
            "domain": "group.softbank",
        },
        {
            "title": "SoftBank reportedly finalizes OpenAI investment with $22.5B cash infusion",
            "url": "https://siliconangle.com/softbank-openai",
            "domain": "siliconangle.com",
        },
        {
            "title": "SoftBank races to fulfill $22.5 billion funding commitment to OpenAI by year-end",
            "url": "https://finance.yahoo.com/news/softbank-openai",
            "domain": "finance.yahoo.com",
        },
    ],
    "default": [
        {
            "title": "検索結果 1：サンプルタイトルが入ります",
            "url": "https://example.com/result1",
            "domain": "example.com",
        },
        {
            "title": "検索結果 2：関連する情報ページ",
            "url": "https://example.org/result2",
            "domain": "example.org",
        },
        {
            "title": "検索結果 3：詳細情報はこちら",
            "url": "https://example.net/result3",
            "domain": "example.net",
        },
        {
            "title": "検索結果 4：公式ドキュメント",
            "url": "https://docs.example.com/guide",
            "domain": "docs.example.com",
        },
    ],
}


# ──────────────────────────────────────────────
# ステップ定義
# ──────────────────────────────────────────────


def _format_results(query: str, results: list[dict]) -> str:
    """検索結果をMarkdown形式に整形する"""
    lines = [f"**検索クエリ:** `{query}`\n"]
    for i, r in enumerate(results, 1):
        lines.append(f"{i}. [{r['title']}]({r['url']})  \n   `{r['domain']}`")
    return "\n".join(lines)


@cl.step(name="🔍 ウェブを検索しました", type="tool", show_input=False)
async def web_search(query: str) -> str:
    """
    ウェブ検索を実行してMarkdown形式の結果を返す。

    - show_input=False：クエリ文字列を入力欄に表示しない
    - type="tool"：ツール呼び出しとしてUIに分類される
    - name に絵文字を入れると視認性が上がる
    """
    # 実際はここでSearchAPIを叩く
    await asyncio.sleep(0.8)

    key = query.lower()
    results = MOCK_SEARCH_DB.get(key, MOCK_SEARCH_DB["default"])
    return _format_results(query, results)


@cl.step(name="🧠 回答を生成中", type="llm", show_input=False)
async def generate_answer(query: str, search_result: str) -> str:
    """
    検索結果をもとに回答を生成する（LLM呼び出しのモック）。

    - type="llm"：LLM処理としてUIに分類される
    - stream_token() を使うとリアルタイムに文字が流れる
    """
    # ── ストリーミングで少しずつ表示 ──────────────────
    answer_text = (
        f"「{query}」について調べた結果をご紹介します。\n\n"
        "検索結果から複数の情報源を確認しました。"
        "各ソースの内容を統合すると、以下のことがわかります：\n\n"
        "- 関連する最新情報が複数のメディアで報告されています\n"
        "- 公式サイトと第三者メディアで内容が一致しています\n"
        "- さらに詳しくは各リンク先をご参照ください\n\n"
        "以上が検索結果のまとめです。"
    )

    # cl.context.current_step で現在のステップを取得してストリーミング
    current_step = cl.context.current_step
    streamed = ""
    for char in answer_text:
        await asyncio.sleep(0.015)  # タイピング感を演出
        streamed += char
        await current_step.stream_token(char)

    return streamed


# ──────────────────────────────────────────────
# メインハンドラ
# ──────────────────────────────────────────────


@cl.on_message
async def main(message: cl.Message) -> None:
    query = message.content

    # Step 1：検索ステップ（折りたたみ表示）
    search_result = await web_search(query)

    # Step 2：LLM回答生成ステップ（ストリーミング）
    answer = await generate_answer(query, search_result)

    # 最終回答をチャットに出力
    await cl.Message(content=answer).send()
