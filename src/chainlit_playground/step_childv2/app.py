"""
Chainlit Step デモ：3階層ネストで調査UIを作る

UIの構造：
  ▼ 🔎 ウェブを調査しています        ← ルートstep（1つだけ）
    ▼ 🔍「基本概念」を調査中          ← 中間step（トピック）
      ▼ 📄 Wikipedia                   ← 末端step（サイト）
      ▼ 📄 公式ドキュメント
    ▼ 🔍「最新動向」を調査中
      ▼ 📄 TechCrunch Japan
      ...
  ▼ ✍️ 情報を集約中
  [最終回答]
"""

import asyncio
import chainlit as cl

# ──────────────────────────────────────────────
# モック：トピックごとの調査サイト一覧
# ──────────────────────────────────────────────

TOPIC_SITES: dict[str, list[dict]] = {
    "基本概念": [
        {"name": "Wikipedia",      "domain": "ja.wikipedia.org",  "summary": "基本的な定義・歴史・関連概念が網羅されています。"},
        {"name": "公式ドキュメント", "domain": "docs.example.com",  "summary": "技術仕様と公式ガイドラインが掲載されています。"},
    ],
    "最新動向": [
        {"name": "TechCrunch Japan", "domain": "jp.techcrunch.com", "summary": "最新リリースと業界トレンドが報告されています。"},
        {"name": "ZDNet Japan",      "domain": "zdnet.com",         "summary": "エンタープライズ向け活用事例が紹介されています。"},
        {"name": "Wired Japan",      "domain": "wired.jp",          "summary": "研究者・開発者のコメントと展望が掲載されています。"},
    ],
    "実用例": [
        {"name": "Qiita", "domain": "qiita.com", "summary": "実装例とサンプルコードが豊富に掲載されています。"},
        {"name": "Zenn",  "domain": "zenn.dev",  "summary": "実務での導入事例と注意点がまとめられています。"},
    ],
}


# ──────────────────────────────────────────────
# 集約・回答生成（@cl.step + ストリーミング）
# ──────────────────────────────────────────────

@cl.step(name="✍️ 情報を集約中", type="llm", show_input=False)
async def aggregate(query: str, all_findings: list[str]) -> str:
    findings_text = "\n".join(f"- {f}" for f in all_findings)
    answer = (
        f"「{query}」について、{len(all_findings)} 件のソースから情報を収集しました。\n\n"
        f"## 調査結果のまとめ\n\n{findings_text}\n\n"
        "---\n各トピックを横断して確認した結果、情報ソース間で大きな矛盾は見られませんでした。"
    )
    current_step = cl.context.current_step
    for char in answer:
        await asyncio.sleep(0.012)
        await current_step.stream_token(char)
    return answer


# ──────────────────────────────────────────────
# メインハンドラ
# ──────────────────────────────────────────────

@cl.on_message
async def main(message: cl.Message) -> None:
    query = message.content
    all_findings: list[str] = []

    # ルートstep：全調査をこの1つに収める
    async with cl.Step(name="🔎 ウェブを調査しています", type="tool") as root_step:
        root_step.input = query
        topics = list(TOPIC_SITES.keys())

        # 中間step（トピック）→ 末端step（サイト）の順にネスト
        # ※ asyncio.gather は別タスクで親コンテキストが切れるため、ここは順次実行
        for topic in topics:
            sites = TOPIC_SITES[topic]

            async with cl.Step(name=f"🔍「{topic}」を調査中", type="tool") as topic_step:
                topic_step.input = f"「{topic}」の観点で調査"

                for site in sites:
                    async with cl.Step(name=f"📄 {site['name']}", type="retrieval") as site_step:
                        site_step.input = site["domain"]
                        await asyncio.sleep(0.4)
                        site_step.output = site["summary"]

                    all_findings.append(f"**[{topic}｜{site['name']}]** {site['summary']}")

                topic_step.output = f"{len(sites)} 件のソースを確認しました"

        root_step.output = f"合計 {len(all_findings)} 件のソースを調査しました"

    # 集約・回答生成
    answer = await aggregate(query, all_findings)
    await cl.Message(content=answer).send()

