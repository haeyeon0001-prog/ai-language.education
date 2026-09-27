#!/usr/bin/env python3
"""index.html（日本語）から en.html / ko.html / zh.html を生成する。

使い方:  python3 i18n/build.py
index.html の文章を変えたら、下の翻訳表に同じ文を追加・修正してから実行する。
翻訳表にない日本語が残っている場合は警告が出る。
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "index.html"

LANGS = {"ja": "index.html", "en": "en.html", "ko": "ko.html", "zh": "zh.html"}

# 各言語で読み込むフォント（日本語ページは元の設定のまま）
FONTS = {
    "en": "Noto+Sans+JP:wght@300;400;500;600;700",
    "ko": "Noto+Sans+KR:wght@300;400;500;600;700&family=Noto+Sans+JP:wght@400;600;700",
    "zh": "Noto+Sans+SC:wght@300;400;500;600;700&family=Noto+Sans+JP:wght@400;600;700",
}
HTML_LANG = {"en": "en", "ko": "ko", "zh": "zh-Hans"}

# (日本語, 英語, 韓国語, 中国語)
T = [
    # ── head / nav / footer
    ("<title>AI✖️言語教育・言語学習</title>",
     "<title>AI × Language Education &amp; Learning</title>",
     "<title>AI × 언어교육・언어학습</title>",
     "<title>AI × 语言教育・语言学习</title>"),
    ('class="nav-logo">AI ✖️ 言語教育</a>',
     'class="nav-logo">AI ✖️ Languages</a>',
     'class="nav-logo">AI ✖️ 언어교육</a>',
     'class="nav-logo">AI ✖️ 语言教育</a>'),
    ('<a href="#about">運営者紹介</a>', '<a href="#about">About</a>', '<a href="#about">운영자 소개</a>', '<a href="#about">关于我</a>'),
    ('<a href="#purpose">このサイトについて</a>', '<a href="#purpose">This Site</a>', '<a href="#purpose">사이트 소개</a>', '<a href="#purpose">关于本站</a>'),
    ('<a href="#books">著書</a>', '<a href="#books">Books</a>', '<a href="#books">저서</a>', '<a href="#books">著作</a>'),
    ('<a href="#apps">アプリ</a>', '<a href="#apps">Apps</a>', '<a href="#apps">앱</a>', '<a href="#apps">应用</a>'),
    ('<a href="#examples">共有例</a>', '<a href="#examples">Examples</a>', '<a href="#examples">활용 사례</a>', '<a href="#examples">实践案例</a>'),
    ("<p>© 2026 白海燕 — AI ✖️ 言語教育・言語学習</p>",
     "<p>© 2026 Haiyan Bai — AI ✖️ Language Education &amp; Learning</p>",
     "<p>© 2026 백해연 — AI ✖️ 언어교육・언어학습</p>",
     "<p>© 2026 白海燕 — AI ✖️ 语言教育・语言学习</p>"),

    # ── hero
    ('<h1 class="fade-in">AI ✖️ 言語教育・言語学習</h1>',
     '<h1 class="fade-in">AI ✖️ Language Education &amp; Learning</h1>',
     '<h1 class="fade-in">AI ✖️ 언어교육・언어학습</h1>',
     '<h1 class="fade-in">AI ✖️ 语言教育・语言学习</h1>'),
    ("語学教員のための AI 活用情報サイト",
     "Practical AI for language teachers",
     "어학 교원을 위한 AI 활용 정보 사이트",
     "面向语言教师的 AI 应用信息网站"),
    ("<strong>白 海燕 博士（学術）</strong>",
     "<strong>Haiyan Bai, Ph.D.</strong>",
     "<strong>백해연 박사(학술)</strong>",
     "<strong>白海燕 博士（学术）</strong>"),

    # ── about
    ('<p class="section-label fade-in">運営者紹介</p>',
     '<p class="section-label fade-in">About</p>',
     '<p class="section-label fade-in">운영자 소개</p>',
     '<p class="section-label fade-in">关于我</p>'),
    ('<h2 class="section-title fade-in">白 海燕　博士（学術）</h2>',
     '<h2 class="section-title fade-in">Haiyan Bai, Ph.D.</h2>',
     '<h2 class="section-title fade-in">백해연 박사(학술)</h2>',
     '<h2 class="section-title fade-in">白海燕 博士（学术）</h2>'),
    ('<p class="section-lead fade-in">Bai Haiyan / 백해연</p>',
     '<p class="section-lead fade-in">白海燕 / 백해연</p>',
     '<p class="section-lead fade-in">白海燕 / Bai Haiyan</p>',
     '<p class="section-lead fade-in">Bai Haiyan / 백해연</p>'),
    ("中国生まれの朝鮮族です。中学校から日本語を学び始め、大学では日本語を専攻しました。その後、日本の大学院に進学し言語学を専攻。数年前には韓国の大学で韓国手話コーパス構築プロジェクトに研究員として参加し、手話の世界にも触れることができました。",
     "I was born in China as a member of the Korean ethnic minority. I began studying Japanese in junior high school, majored in Japanese at university, and then went on to graduate school in Japan to study linguistics. A few years ago I joined a Korean Sign Language corpus project at a university in Korea as a researcher, which also opened the world of sign language to me.",
     "중국에서 태어난 조선족입니다. 중학교 때부터 일본어를 배우기 시작해 대학에서는 일본어를 전공했습니다. 그 후 일본의 대학원에 진학해 언어학을 전공했습니다. 몇 년 전에는 한국의 대학에서 한국수어 코퍼스 구축 프로젝트에 연구원으로 참여하며 수어의 세계도 접할 수 있었습니다.",
     "我是出生在中国的朝鲜族。从初中开始学习日语，大学主修日语，之后赴日本读研究生，专攻语言学。几年前，我曾以研究员身份参与韩国一所大学的韩国手语语料库建设项目，也因此接触到了手语的世界。"),
    ("言葉を考え、学ぶことが好きで、日常的にさまざまな言語に触れながら過ごしてきました。現在は大学で中国語・韓国語・日本語を教えながら、言葉のなぜを知るために掘り下げたものを論文にしたり、どうすれば言語をより速く習得できるか、教える側と学ぶ側の両方の効率をどう上げられるかを日々模索しています。",
     "I love thinking about and learning languages, and I live surrounded by many of them every day. I now teach Chinese, Korean and Japanese at university. I write papers that dig into the “why” behind language, and every day I look for ways to help people acquire languages faster, making both teaching and learning more efficient.",
     "말에 대해 생각하고 배우는 것을 좋아해서, 일상적으로 다양한 언어를 접하며 지내 왔습니다. 현재는 대학에서 중국어・한국어・일본어를 가르치면서, 언어의 ‘왜’를 알기 위해 파고든 것을 논문으로 쓰기도 하고, 어떻게 하면 언어를 더 빨리 습득할 수 있을지, 가르치는 쪽과 배우는 쪽 모두의 효율을 어떻게 높일 수 있을지 매일 모색하고 있습니다.",
     "我喜欢思考和学习语言，日常生活中一直接触着各种语言。目前我在大学教授汉语、韩语和日语，一边把为探究语言“为什么”而深入研究的内容写成论文，一边每天摸索如何更快地掌握语言，以及如何同时提高教与学双方的效率。"),
    ('<p class="meta-label">言語</p>', '<p class="meta-label">Languages</p>', '<p class="meta-label">언어</p>', '<p class="meta-label">语言</p>'),
    ("韓国・朝鮮語と中国語のバイリンガル、日本語、英語",
     "Bilingual in Korean and Chinese; also Japanese and English",
     "한국・조선어와 중국어 이중언어 화자, 일본어, 영어",
     "韩国・朝鲜语与汉语双语，日语，英语"),
    ('<p class="meta-label">教育歴</p>', '<p class="meta-label">Teaching</p>', '<p class="meta-label">교육 경력</p>', '<p class="meta-label">教学经历</p>'),
    ("大学での韓国語・中国語・日本語教育に従事",
     "Teaches Korean, Chinese and Japanese at university",
     "대학에서 한국어・중국어・일본어 교육에 종사",
     "在大学从事韩语、汉语、日语教学"),
    ('<p class="meta-label">AI 応用</p>', '<p class="meta-label">AI in Practice</p>', '<p class="meta-label">AI 활용</p>', '<p class="meta-label">AI 应用</p>'),
    ("授業設計・教材作成・学習支援へのAI活用を実践中。G検定（JDLA）取得。",
     "Applies AI to course design, materials creation and learner support. JDLA Deep Learning for General (G-Kentei) certified.",
     "수업 설계・교재 제작・학습 지원에 AI를 활용하고 있습니다. G검정(JDLA) 취득.",
     "在课程设计、教材编写和学习支持中实践 AI 应用。持有 JDLA G 检定资格。"),
    ("研究業績を見る <span", "View research profile <span", "연구 업적 보기 <span", "查看研究成果 <span"),

    # ── purpose
    ('<p class="section-label fade-in">このサイトについて</p>',
     '<p class="section-label fade-in">This Site</p>',
     '<p class="section-label fade-in">사이트 소개</p>',
     '<p class="section-label fade-in">关于本站</p>'),
    ("AIで、教える時間を<br>もっと価値あるものに。",
     "Let AI make teaching time<br>more valuable.",
     "AI로, 가르치는 시간을<br>더 가치 있게.",
     "用 AI，让教学时间<br>更有价值。"),
    ("語学教員の仕事には反復的な作業が多くあります。AIを活用することで、そうした作業を効率化し、空いた時間を授業の改善や学生との対話に充てる。このサイトでは、私自身が試しているAI活用の方法やツールを具体的に共有していきます。",
     "Language teaching involves a lot of repetitive work. With AI, that work becomes faster, and the time saved can go into better lessons and conversations with students. On this site I share, in concrete terms, the AI methods and tools I use myself.",
     "어학 교원의 업무에는 반복적인 작업이 많습니다. AI를 활용해 그런 작업을 효율화하고, 남는 시간을 수업 개선과 학생과의 대화에 씁니다. 이 사이트에서는 제가 직접 시도하고 있는 AI 활용 방법과 도구를 구체적으로 공유합니다.",
     "语言教师的工作中有大量重复性任务。借助 AI 提高这些工作的效率，把节省下来的时间用于改进课堂和与学生交流。本站将具体分享我本人正在尝试的 AI 应用方法和工具。"),
    ("<h3>反復作業を減らす</h3>", "<h3>Less repetitive work</h3>", "<h3>반복 작업 줄이기</h3>", "<h3>减少重复劳动</h3>"),
    ("問題作成、採点補助、語彙リスト整理など、繰り返しの多い作業をAIで省力化。手を動かす時間を、考える時間に変えます。",
     "Let AI handle repetitive tasks such as writing exercises, assisting with grading and organizing vocabulary lists, turning time spent on busywork into time for thinking.",
     "문제 작성, 채점 보조, 어휘 목록 정리 등 반복이 많은 작업을 AI로 줄입니다. 손을 움직이는 시간을 생각하는 시간으로 바꿉니다.",
     "出题、辅助批改、整理词汇表等重复性工作交给 AI，把动手的时间变成思考的时间。"),
    ("<h3>資料作成を時短する</h3>", "<h3>Faster materials</h3>", "<h3>자료 제작 시간 단축</h3>", "<h3>更快地制作资料</h3>"),
    ("スライド、配布物、音声教材の作成にAIを活用。準備時間を大幅に削減し、授業の質に集中できる環境をつくります。",
     "Use AI to create slides, handouts and audio materials, cutting preparation time dramatically so you can focus on the quality of your lessons.",
     "슬라이드, 배포 자료, 음성 교재 제작에 AI를 활용합니다. 준비 시간을 크게 줄여 수업의 질에 집중할 수 있는 환경을 만듭니다.",
     "在制作幻灯片、讲义和音频教材时运用 AI，大幅缩短备课时间，专注于提升课堂质量。"),

    # ── books
    ('<p class="section-label fade-in">著書</p>', '<p class="section-label fade-in">Books</p>', '<p class="section-label fade-in">저서</p>', '<p class="section-label fade-in">著作</p>'),
    ("AIとつくった教科書。", "Textbooks made with AI.", "AI와 함께 만든 교재.", "与 AI 一起打造的教材。"),
    ("授業での実践をもとに、AIを活用して企画・執筆・音声制作まで行った教科書です。多くの本に音声と練習アプリがついていて、スマートフォンからすぐに学習できます。表紙をクリックするとAmazonのページが開きます。",
     "Based on classroom practice, these textbooks were planned, written and given audio with the help of AI. Most come with audio and a practice app, so you can start learning right away on your smartphone. The books are in Japanese; click a cover to open its Amazon page.",
     "수업 실천을 바탕으로 AI를 활용해 기획・집필・음성 제작까지 한 교재입니다. 대부분의 책에 음성과 연습 앱이 있어 스마트폰으로 바로 학습할 수 있습니다. 책은 일본어로 쓰여 있으며, 표지를 클릭하면 Amazon 페이지가 열립니다.",
     "这些教材基于课堂实践，借助 AI 完成了策划、写作和音频制作。大多数书都配有音频和练习应用，用手机即可马上学习。书籍为日文版，点击封面即可打开亚马逊页面。"),
    ('<p class="book-lang">韓国語 × 漢字</p>', '<p class="book-lang">Korean × Kanji</p>', '<p class="book-lang">한국어 × 한자</p>', '<p class="book-lang">韩语 × 汉字</p>'),
    ('<p class="book-lang">韓国語</p>', '<p class="book-lang">Korean</p>', '<p class="book-lang">한국어</p>', '<p class="book-lang">韩语</p>'),
    ('<p class="book-lang">中国語</p>', '<p class="book-lang">Chinese</p>', '<p class="book-lang">중국어</p>', '<p class="book-lang">汉语</p>'),
    ('<p class="book-lang">日中韓 対照</p>', '<p class="book-lang">Japanese・Chinese・Korean</p>', '<p class="book-lang">한중일 대조</p>', '<p class="book-lang">中日韩对比</p>'),

    ('<p class="book-sub">55字で読み解く、芋づる式漢字語学習</p>',
     '<p class="book-sub">Korean Through Kanji: Introductory — Sino-Korean words chained from 55 characters</p>',
     '<p class="book-sub">한자에서 넓어지는 한국어의 세계 입문편 — 55자로 읽어 내는 줄줄이 한자어 학습</p>',
     '<p class="book-sub">从汉字拓展的韩语世界・入门篇——以 55 个汉字串联学习汉字词</p>'),
    ("「人（인）」など基本の55字から、韓国語の漢字語を芋づる式に覚える入門編。TOPIK1〜4級の語彙に対応。練習アプリつき。",
     "Starting from 55 basic characters such as 人 (인), learn Sino-Korean vocabulary in connected chains. Covers TOPIK levels 1–4, with a practice app.",
     "‘人(인)’ 등 기본 55자에서 한국어 한자어를 줄줄이 익히는 입문편. TOPIK 1~4급 어휘 대응. 연습 앱 포함.",
     "从“人（인）”等 55 个基本汉字出发，串联式记忆韩语汉字词的入门篇。对应 TOPIK 1～4 级词汇，附练习应用。"),
    ('<p class="book-sub">199字で読み解く漢字語</p>',
     '<p class="book-sub">Korean Through Kanji: Intermediate — reading Sino-Korean words with 199 characters</p>',
     '<p class="book-sub">한자에서 넓어지는 한국어의 세계 중급편 — 199자로 읽어 내는 한자어</p>',
     '<p class="book-sub">从汉字拓展的韩语世界・中级篇——用 199 个汉字读懂汉字词</p>'),
    ("199字の漢字音を手がかりに、中級レベルの漢字語を体系的に広げていく一冊。TOPIK1〜4級語彙、練習アプリつき。",
     "Using the readings of 199 characters as clues, systematically expand your intermediate Sino-Korean vocabulary. TOPIK levels 1–4, with a practice app.",
     "199자의 한자음을 실마리로 중급 수준의 한자어를 체계적으로 넓혀 가는 책. TOPIK 1~4급 어휘, 연습 앱 포함.",
     "以 199 个汉字的读音为线索，系统扩展中级汉字词。对应 TOPIK 1～4 级词汇，附练习应用。"),
    ('<p class="book-sub">接辞24字で広がる漢字語</p>',
     '<p class="book-sub">Korean Through Kanji: Affixes — Sino-Korean words built from 24 affixes</p>',
     '<p class="book-sub">한자에서 넓어지는 한국어의 세계 접사편 — 접사 24자로 넓어지는 한자어</p>',
     '<p class="book-sub">从汉字拓展的韩语世界・词缀篇——24 个词缀扩展汉字词</p>'),
    ("「的」「性」などの接辞24字で、漢字語を一気に何倍にも増やす接辞編。TOPIK1〜4級語彙、練習アプリつき。",
     "With 24 affixes such as 的 and 性, multiply your Sino-Korean vocabulary many times over. TOPIK levels 1–4, with a practice app.",
     "‘的’, ‘性’ 등 접사 24자로 한자어를 단숨에 몇 배로 늘리는 접사편. TOPIK 1~4급 어휘, 연습 앱 포함.",
     "借助“的”“性”等 24 个词缀，让汉字词量成倍增长的词缀篇。对应 TOPIK 1～4 级词汇，附练习应用。"),
    ('<p class="book-sub">音声60トラック・復習アプリつき</p>',
     '<p class="book-sub">Level Up in 3 Months: Korean, Cooking Edition — 60 audio tracks and a review app</p>',
     '<p class="book-sub">3개월 레벨업 한국어 요리편 — 음성 60트랙・복습 앱 포함</p>',
     '<p class="book-sub">3 个月提升韩语・料理篇——60 段音频，附复习应用</p>'),
    ("キムチチャーハン、ビビンバ、トックク……季節の韓国料理12品で会話と文法を学ぶ全12課。初中級レベル。",
     "Kimchi fried rice, bibimbap, tteokguk… 12 lessons that teach conversation and grammar through 12 seasonal Korean dishes. Upper-beginner level.",
     "김치볶음밥, 비빔밥, 떡국… 계절의 한국 요리 12가지로 회화와 문법을 배우는 전 12과. 초중급 수준.",
     "泡菜炒饭、拌饭、年糕汤……通过 12 道时令韩国料理学习会话和语法，共 12 课。初中级水平。"),
    ('<p class="book-sub">HSK3〜4級レベル</p>',
     '<p class="book-sub">Level Up in 3 Months: Chinese, Cooking Edition — HSK levels 3–4</p>',
     '<p class="book-sub">3개월 레벨업 중국어 요리편 — HSK 3~4급 수준</p>',
     '<p class="book-sub">3 个月提升汉语・料理篇——HSK 3～4 级水平</p>'),
    ("餃子、麻婆豆腐、北京ダック、火鍋など中国各地の料理12品で学ぶ全12課。本文音声93本、単語カード282語の練習アプリつき。",
     "Dumplings, mapo tofu, Peking duck, hot pot… 12 lessons built around 12 dishes from across China. 93 audio tracks and a practice app with 282 vocabulary cards.",
     "만두, 마파두부, 베이징 덕, 훠궈 등 중국 각지의 요리 12가지로 배우는 전 12과. 본문 음성 93개, 단어 카드 282개의 연습 앱 포함.",
     "饺子、麻婆豆腐、北京烤鸭、火锅……通过中国各地 12 道菜学习，共 12 课。附 93 段课文音频和含 282 张单词卡的练习应用。"),
    ('<p class="book-sub">点と、線 ― 日中韓 同形漢字語の物語</p>',
     '<p class="book-sub">Kanji, Lost Three Times — dots and lines: stories of kanji words shared by Japanese, Chinese and Korean</p>',
     '<p class="book-sub">한자, 세 번 헤매다 — 점과 선: 한중일 동형 한자어 이야기</p>',
     '<p class="book-sub">汉字，三度迷途——点与线：中日韩同形汉字词的故事</p>'),
    ("同じ漢字語が、中国語・日本語・韓国語でどう意味を変えるのか。「老婆」をはじめ、三つの言語を行き来する漢字語の物語。",
     "How does the same kanji word change its meaning across Chinese, Japanese and Korean? Starting with 老婆, stories of words that travel between the three languages.",
     "같은 한자어가 중국어・일본어・한국어에서 어떻게 의미가 달라질까. ‘老婆’를 비롯해 세 언어를 오가는 한자어 이야기.",
     "同一个汉字词在汉语、日语、韩语中意义如何变化？从“老婆”说起，讲述穿梭于三种语言之间的汉字词故事。"),
    (">Amazonで見る</a>", ">View on Amazon</a>", ">Amazon에서 보기</a>", ">在亚马逊查看</a>"),
    (">練習アプリ</a>", ">Practice app</a>", ">연습 앱</a>", ">练习应用</a>"),
    (">音声・アプリ</a>", ">Audio &amp; app</a>", ">음성・앱</a>", ">音频・应用</a>"),
    ("Amazonで著書をすべて見る <span", "See all books on Amazon <span", "Amazon에서 저서 모두 보기 <span", "在亚马逊查看全部著作 <span"),

    # ── apps
    ('<p class="section-label fade-in">アプリ</p>', '<p class="section-label fade-in">Apps</p>', '<p class="section-label fade-in">앱</p>', '<p class="section-label fade-in">应用</p>'),
    ("AIでつくった学習アプリ。", "Learning apps built with AI.", "AI로 만든 학습 앱.", "用 AI 打造的学习应用。"),
    ("授業や自分の学習のために、AIと一緒に開発したWebアプリです。インストール不要で、スマートフォンのブラウザからそのまま使えます。ホーム画面に追加すればアプリのように起動できます。",
     "Web apps I developed together with AI for my classes and my own study. No installation needed: they run right in your smartphone browser, and you can add them to your home screen to launch them like an app. The interface is mainly in Japanese.",
     "수업과 저 자신의 학습을 위해 AI와 함께 개발한 웹 앱입니다. 설치가 필요 없고 스마트폰 브라우저에서 바로 쓸 수 있습니다. 홈 화면에 추가하면 앱처럼 실행할 수 있습니다. 화면은 주로 일본어입니다.",
     "这些是我为课堂和自身学习与 AI 一起开发的网页应用。无需安装，用手机浏览器即可直接使用；添加到主屏幕后可像应用一样启动。界面主要为日文。"),
    ('<p class="app-group-title fade-in">発音</p>', '<p class="app-group-title fade-in">Pronunciation</p>', '<p class="app-group-title fade-in">발음</p>', '<p class="app-group-title fade-in">发音</p>'),
    ('<p class="app-group-title fade-in">教科書と連動</p>', '<p class="app-group-title fade-in">Textbook companions</p>', '<p class="app-group-title fade-in">교재 연동</p>', '<p class="app-group-title fade-in">教材配套</p>'),
    ("🔒 教科書と連動したアプリは、登録した方のみご覧いただけます。Googleアカウントでログインし、初回のみ氏名と所属をご登録ください。",
     "🔒 The textbook companion apps are available to registered users only. Sign in with your Google account and, the first time only, register your full name and affiliation.",
     "🔒 교재 연동 앱은 등록한 분만 보실 수 있습니다. Google 계정으로 로그인하고, 처음 한 번만 실명과 소속을 등록해 주세요.",
     "🔒 教材配套应用仅限注册用户查看。请使用 Google 账号登录，首次登录时登记真实姓名和所属单位。"),
    ('id="companion-login" href="account/login.html">Googleでログイン</a>',
     'id="companion-login" href="account/login.html">Sign in with Google</a>',
     'id="companion-login" href="account/login.html">Google로 로그인</a>',
     'id="companion-login" href="account/login.html">使用 Google 登录</a>'),
    ('<p class="app-group-title fade-in">英語</p>', '<p class="app-group-title fade-in">English</p>', '<p class="app-group-title fade-in">영어</p>', '<p class="app-group-title fade-in">英语</p>'),
    ("<h3>韓国語 発音マスター</h3>", "<h3>Korean Pronunciation Master</h3>", "<h3>한국어 발음 마스터</h3>", "<h3>韩语发音大师</h3>"),
    ("子音19・母音21、パッチム、平音・激音・濃音の聞き分け、字母の組み立てゲーム。手本を聞いて自分の声を録音し、比べて確認できます。",
     "19 consonants and 21 vowels, final consonants (batchim), telling lax, aspirated and tense sounds apart, and a letter-building game. Listen to a model, record yourself and compare.",
     "자음 19・모음 21, 받침, 평음・격음・경음 구별, 자모 조립 게임. 모범 발음을 듣고 자신의 목소리를 녹음해 비교할 수 있습니다.",
     "19 个辅音、21 个元音、收音，平音・送气音・紧音辨别，以及字母拼合游戏。听示范、录下自己的声音进行对比。"),
    ("<h3>連音化アニメーション</h3>", "<h3>Liaison Animation</h3>", "<h3>연음화 애니메이션</h3>", "<h3>连音化动画</h3>"),
    ("パッチムが次の音節へ流れていく様子をアニメーションで表示。韓国語の発音変化のしくみを目で見て理解できます。",
     "Animations show how a final consonant flows into the next syllable, so you can see how Korean sound changes work.",
     "받침이 다음 음절로 넘어가는 모습을 애니메이션으로 보여 줍니다. 한국어 발음 변화의 원리를 눈으로 보며 이해할 수 있습니다.",
     "用动画展示收音如何流向下一个音节，直观理解韩语发音变化的规律。"),
    ("<h3>中国語 発音練習</h3>", "<h3>Chinese Pronunciation Practice</h3>", "<h3>중국어 발음 연습</h3>", "<h3>汉语发音练习</h3>"),
    ("4つの声調、二字の声調の組み合わせ、基本50単語を練習。自分の発音をAIが採点します。",
     "Practice the four tones, two-syllable tone pairs and 50 basic words. AI scores your pronunciation.",
     "4개의 성조, 두 글자 성조 조합, 기본 50단어를 연습합니다. AI가 발음을 채점합니다.",
     "练习四个声调、双音节声调组合和 50 个基本词语，由 AI 为你的发音打分。"),
    ("<h3>韓国語 料理編 音声・復習アプリ</h3>", "<h3>Korean Cooking Edition: Audio &amp; Review App</h3>", "<h3>한국어 요리편 음성・복습 앱</h3>", "<h3>韩语料理篇 音频・复习应用</h3>"),
    ("全12課・60トラックの音声と、ことばカード・文法・書き取りの復習アプリ。本の各課のQRコードからも開けます。",
     "Audio for all 12 lessons (60 tracks) plus a review app with word cards, grammar and dictation. Also opens from the QR code in each lesson of the book.",
     "전 12과・60트랙의 음성과 단어 카드・문법・받아쓰기 복습 앱. 책의 각 과 QR 코드로도 열 수 있습니다.",
     "全 12 课、60 段音频，以及单词卡、语法、听写复习应用。也可通过书中各课的二维码打开。"),
    ("<h3>中国語 料理編 音声・練習アプリ</h3>", "<h3>Chinese Cooking Edition: Audio &amp; Practice App</h3>", "<h3>중국어 요리편 음성・연습 앱</h3>", "<h3>汉语料理篇 音频・练习应用</h3>"),
    ("本文音声93本、単語カード282語、4択クイズ、書き取り。話者ごと・ゆっくり版の音声も収録しています。",
     "93 audio tracks, 282 word cards, multiple-choice quizzes and dictation. Includes per-speaker and slow-speed audio.",
     "본문 음성 93개, 단어 카드 282개, 4지선다 퀴즈, 받아쓰기. 화자별・느린 버전 음성도 수록했습니다.",
     "93 段课文音频、282 张单词卡、四选一测验和听写。还收录了分角色和慢速版音频。"),
    ("<h3>漢字から広がる韓国語の世界 練習アプリ</h3>", "<h3>Korean Through Kanji: Practice App</h3>", "<h3>한자에서 넓어지는 한국어의 세계 연습 앱</h3>", "<h3>从汉字拓展的韩语世界 练习应用</h3>"),
    ("入門編・中級編・接辞編に対応。漢字ドリル・漢字探し・漢字⇔ハングルのマッチング・文章穴埋めの4モードで、韓国語の漢字語を身につけます。",
     "Covers the Introductory, Intermediate and Affixes volumes. Four modes — kanji drills, kanji search, kanji ⇔ Hangul matching and sentence fill-in-the-blank — build your Sino-Korean vocabulary.",
     "입문편・중급편・접사편 대응. 한자 드릴・한자 찾기・한자⇔한글 매칭・문장 빈칸 채우기의 4가지 모드로 한국어 한자어를 익힙니다.",
     "对应入门篇、中级篇、词缀篇。通过汉字练习、找汉字、汉字⇔韩文配对、句子填空四种模式掌握韩语汉字词。"),
    ("Part 1〜3の模擬試験、約300問・キューカード45枚。音声入力とAI音声の読み上げで、スピーキングを一人で練習できます。",
     "Mock tests for Parts 1–3 with about 300 questions and 45 cue cards. Voice input and AI read-aloud let you practice speaking on your own.",
     "Part 1~3 모의시험, 약 300문항・큐카드 45장. 음성 입력과 AI 음성 낭독으로 스피킹을 혼자 연습할 수 있습니다.",
     "Part 1～3 模拟考试，约 300 道题、45 张话题卡。借助语音输入和 AI 朗读，一个人也能练习口语。"),
    ("<h3>IELTS 統合学習アプリ</h3>", "<h3>IELTS All-in-One Study App</h3>", "<h3>IELTS 통합 학습 앱</h3>", "<h3>IELTS 综合学习应用</h3>"),
    ("短文暗記カリキュラム、弱点補強、速読、ライティング添削、学習統計。毎日の学習を一か所で管理します。",
     "Sentence memorization curriculum, weak-point training, speed reading, writing feedback and study statistics — manage your daily study in one place.",
     "짧은 문장 암기 커리큘럼, 약점 보강, 속독, 라이팅 첨삭, 학습 통계. 매일의 학습을 한곳에서 관리합니다.",
     "短句背诵课程、弱项强化、速读、写作批改和学习统计，在一处管理每天的学习。"),
    ("90日間の英語学習プログラム。オーストラリア・ニュージーランド英語の音声で、作文とテストを積み重ねていきます。",
     "A 90-day English program. Build up writing and tests step by step with Australian and New Zealand English audio.",
     "90일간의 영어 학습 프로그램. 호주・뉴질랜드 영어 음성으로 작문과 테스트를 차곡차곡 쌓아 갑니다.",
     "为期 90 天的英语学习计划。借助澳大利亚和新西兰英语音频，逐步积累写作与测验。"),
    ('<span class="tag sakura">韓国語</span>', '<span class="tag sakura">Korean</span>', '<span class="tag sakura">한국어</span>', '<span class="tag sakura">韩语</span>'),
    ('<span class="tag sky">中国語</span>', '<span class="tag sky">Chinese</span>', '<span class="tag sky">중국어</span>', '<span class="tag sky">汉语</span>'),
    ('<span class="tag sky">英語</span>', '<span class="tag sky">English</span>', '<span class="tag sky">영어</span>', '<span class="tag sky">英语</span>'),
    ('<span class="app-open">開く ›</span>', '<span class="app-open">Open ›</span>', '<span class="app-open">열기 ›</span>', '<span class="app-open">打开 ›</span>'),

    # ── examples
    ('<p class="section-label fade-in">共有例</p>', '<p class="section-label fade-in">Examples</p>', '<p class="section-label fade-in">활용 사례</p>', '<p class="section-label fade-in">实践案例</p>'),
    ("実際に使っている方法。", "Methods I actually use.", "실제로 쓰고 있는 방법.", "我实际在用的方法。"),
    ("授業や準備で活用している例です。今後も随時追加していきます。",
     "Examples from my own teaching and preparation. More will be added over time.",
     "수업과 준비에 활용하고 있는 사례입니다. 앞으로도 수시로 추가해 나가겠습니다.",
     "这些是我在授课和备课中运用的例子，今后会不断补充。"),
    ('<span class="example-badge tool">ツール</span>', '<span class="example-badge tool">Tool</span>', '<span class="example-badge tool">도구</span>', '<span class="example-badge tool">工具</span>'),
    ('<span class="example-badge material">教材</span>', '<span class="example-badge material">Materials</span>', '<span class="example-badge material">교재</span>', '<span class="example-badge material">教材</span>'),
    ('<span class="example-badge workflow">ワークフロー</span>', '<span class="example-badge workflow">Workflow</span>', '<span class="example-badge workflow">워크플로</span>', '<span class="example-badge workflow">工作流程</span>'),
    ("ChatGPT / Claude を使った韓国語・中国語の練習問題自動生成",
     "Generating Korean and Chinese practice exercises with ChatGPT / Claude",
     "ChatGPT / Claude를 활용한 한국어・중국어 연습 문제 자동 생성",
     "使用 ChatGPT / Claude 自动生成韩语、汉语练习题"),
    ("AIで作成した語彙リスト・単語帳テンプレート",
     "Vocabulary lists and flashcard templates made with AI",
     "AI로 만든 어휘 목록・단어장 템플릿",
     "用 AI 制作的词汇表和单词本模板"),
    ("学生の作文に対するAIフィードバックの活用方法",
     "Using AI feedback on student compositions",
     "학생 작문에 대한 AI 피드백 활용 방법",
     "针对学生作文的 AI 反馈运用方法"),
    ("AIを使った授業スライドの効率的な作成手順",
     "An efficient workflow for building lesson slides with AI",
     "AI를 활용한 수업 슬라이드의 효율적인 제작 절차",
     "用 AI 高效制作课堂幻灯片的步骤"),
    ("TTS（テキスト読み上げ）によるリスニング教材の作成",
     "Creating listening materials with TTS (text-to-speech)",
     "TTS(텍스트 음성 변환)를 활용한 듣기 교재 제작",
     "利用 TTS（文本转语音）制作听力教材"),
    ("試験問題のバリエーション自動生成と整理",
     "Generating and organizing variations of exam questions",
     "시험 문제 변형의 자동 생성과 정리",
     "自动生成并整理试题的多种变体"),
]

# 『書名』を含む属性（書名は日本語の原題のまま）
ATTR = {
    "en": [(r'aria-label="『(.+?)』をAmazonで見る"', r'aria-label="View “\1” on Amazon"'),
           (r'alt="『(.+?)』表紙"', r'alt="Cover of “\1”"')],
    "ko": [(r'aria-label="『(.+?)』をAmazonで見る"', r'aria-label="『\1』 Amazon에서 보기"'),
           (r'alt="『(.+?)』表紙"', r'alt="『\1』 표지"')],
    "zh": [(r'aria-label="『(.+?)』をAmazonで見る"', r'aria-label="在亚马逊查看《\1》"'),
           (r'alt="『(.+?)』表紙"', r'alt="《\1》封面"')],
}

PILLS_RE = re.compile(r'<div class="lang-pills">.*?</div>', re.S)


def pills(active):
    items = []
    for code, label in (("ja", "JP"), ("en", "EN"), ("ko", "KO"), ("zh", "ZH")):
        cls = ' class="active" aria-current="page"' if code == active else ""
        items.append(f'      <a href="{LANGS[code]}" hreflang="{code}" lang="{code}"{cls}>{label}</a>')
    return '<div class="lang-pills">\n' + "\n".join(items) + "\n    </div>"


def alternates():
    links = [f'<link rel="alternate" hreflang="{c}" href="https://baihaiyan.com/{"" if f == "index.html" else f}">'
             for c, f in LANGS.items()]
    links.append('<link rel="alternate" hreflang="x-default" href="https://baihaiyan.com/">')
    return "\n".join(links)


def with_head(html):
    html = re.sub(r'\n<link rel="alternate"[^\n]*', "", html)
    return html.replace("</title>", "</title>\n" + alternates(), 1)


def main():
    ja = SRC.read_text(encoding="utf-8")
    ja = with_head(PILLS_RE.sub(pills("ja"), ja))
    SRC.write_text(ja, encoding="utf-8")

    col = {"en": 1, "ko": 2, "zh": 3}
    pairs = sorted(T, key=lambda r: len(r[0]), reverse=True)
    ok = True
    for lang, i in col.items():
        html = ja.replace('<html lang="ja">', f'<html lang="{HTML_LANG[lang]}">', 1)
        html = html.replace("Noto+Sans+JP:wght@300;400;500;600;700", FONTS[lang], 1)
        html = PILLS_RE.sub(pills(lang), html)
        for row in pairs:
            if row[0] not in html:
                print(f"[{lang}] 見つからない: {row[0][:40]}", file=sys.stderr)
                ok = False
            html = html.replace(row[0], row[i])
        for pat, rep in ATTR[lang]:
            html = re.sub(pat, rep, html)

        # 翻訳漏れチェック（<style>・書名・URL以外に日本語のかな・漢字が残っていないか）
        body = re.sub(r"<style>.*?</style>", "", html, flags=re.S)
        body = re.sub(r"<script[^>]*>.*?</script>", "", body, flags=re.S)
        body = re.sub(r'(href|src)="[^"]*"', "", body)
        body = re.sub(r'<h3 class="book-title">.*?</h3>', "", body)
        body = re.sub(r"[“『《].*?[”』》]", "", body)
        if lang == "en":
            left = re.findall(r"[^\x00-\x7f“”’—–…×✖️⇔›→〜～・々]*[ぁ-んァ-ヶ][^<]*", body)
        else:
            left = re.findall(r"[^<>]*[ぁ-んァ-ヶ][^<>]*", body)
        left = [s.strip() for s in left if s.strip() and s.strip() not in ("白海燕 / 백해연", "白 海燕", "『")]
        if left:
            ok = False
            for s in left:
                print(f"[{lang}] 翻訳漏れ?: {s[:60]}", file=sys.stderr)
        (ROOT / LANGS[lang]).write_text(html, encoding="utf-8")
        print(f"wrote {LANGS[lang]}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
