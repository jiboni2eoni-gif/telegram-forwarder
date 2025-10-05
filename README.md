# Telegram Forwarder Bot (Customized for your channels)

This package is pre-configured with your channel IDs:
- Source: -1002856470667 (DeshiviralHubLink(Bot))
- Targets: -1003172610238 (DeshiviralHub_All), -1003116951675 (DeshiviralHub (Latest))

How to use:
1. Update config.yaml: set bot_token to your token.
2. Add more routes in config.yaml under 'routes' as needed.
3. For local testing, run:
   pip install -r requirements.txt
   python poller.py

4. For production (Render.com), push to GitHub and create a Web Service. Start command: gunicorn app:app

Adding filters later:
- Edit config.yaml -> add 'keywords' or 'hashtags' for new routes.
- The bot auto-reloads config.yaml every 30 seconds (no restart needed).

Security:
- Keep bot token secret. Do NOT commit it to public repo.



















একদম সংক্ষিপ্ত সারসংক্ষেপ

সব কনফিগ config.json (বা config.yaml) এ রাখো — চ্যানেল ID, রুটস, ফিল্টার, moderation flag ইত্যাদি।

GitHub-এ ফাইল edit → commit করলেই Render auto-deploy করবে।

Deploy হলে টেস্ট করতে Source চ্যানেলে পোস্ট দাও → Render logs চেক করো।

সমস্যা হলে commit revert করে আগের অবস্থায় ফিরো (GitHub UI-তে আছে)।

নীচে পুরো কাজটা ধাপে ধাপে, পিক্স-মতো (copy-paste করতে পারবে) দিলাম।

1) config ফাইল (structure — GitHub এ রাখবে)

প্রস্তাবিত config.json (তুমি আগে দিয়েছো না — তাই আমি সুস্পষ্ট একটি রাখলাম)। Repo-র root-এ এই ফাইল রাখো:

{
  "source_channels": [
    -1002856470667
  ],
  "destination_channels": {
    "all": [
      -1003172610238,
      -1003116951675
    ],
    "deshi": [],
    "indian": [],
    "japan": []
  },
  "filters": {
    "deshi": ["বাংলা", "deshi", "bangla"],
    "indian": ["india", "hindi", "bollywood"],
    "japan": ["japan", "anime"]
  },
  "default_route": "all",
  "moderation_mode": false,
  "moderator_chat": "@your_moderator_channel"
}


নোট:

Channel ID গুলো -100... ফরম্যাটে হবে (private)। public হলে @channelusername দিতে পারো (string)।

filters হলো শব্দভিত্তিক (substring) মিল — পরে regex চাইলে ঐ অংশ code-এ বদল করে নেবে।

2) কিভাবে নতুন channel যোগ/মুছবে (GitHub web UI দিয়ে — সবচেয়ে সহজ)
A — GitHub Web UI (quickest)

আপনার repo খুলো → config.json ক্লিক করে Edit this file (পেন্সিল আইকন) চাপো।

নতুন destination_channels এ নতুন ID যোগ করো, উদাহরণ:

"japan": [
  -1009999999999
]


— অথবা all লিস্টে যোগ করতে চাইলে:

"all": [
  -1003172610238,
  -1003116951675,
  -1009999999999
]


নিচে “Commit changes” লিখে Commit directly to the main branch সিলেক্ট করে Commit করো।

Render auto-deploy করবে (অথবা তুমি Manual deploy চাপতে পারো) — কয়েক সেকেন্ডে সার্ভার আপডেট হবে।

B — Git CLI (local → push)
git checkout -b add-japan
# edit config.json with your editor
git add config.json
git commit -m "Add japan route and target channel"
git push origin add-japan
# Then open GitHub and create PR -> merge to main (or push to main directly)

3) কিভাবে keyword / filter যোগ/বদল করবে

config.json-এর filters সেকশনে নতুন কী-ওয়ার্ড যোগ করো বা remove করো:

উদাহরণ — নতুন keyword যোগ (deshi)

"filters": {
  "deshi": ["বাংলা", "deshi", "bangla", "চলচ্চিত্র"],
  ...
}


Commit করলেই Render auto-deploy করবে এবং নতুন নিয়ম কার্যকর হবে। (তুমি চাইলে config_reload_seconds রেখে auto-reload কোড করলে redeploy ছাড়া পড়বে — কিন্তু আমাদের Render/Docker সেটআপে redeploy হয়েই কাজ করবে।)

4) moderation চালু/বন্ধ করা

config.json-এ

"moderation_mode": true,
"moderator_chat": "@DeshiviralHub_Moderator"


true করলে সব পোস্ট moderator chat-এ copy হবে ও DB তে moderation_queue এ জমা হবে; moderator পরে approve করলে forward হবে (approve logic থাকলে)।

false করলে সরাসরি forward হবে।

Commit → redeploy → test.

5) private channel ID কীভাবে পাবে — দ্রুত স্মরণ

Bot-কে target/private channel-এ Admin হিসেবে যোগ করো (Post permission)।

channel এ নতুন পোস্ট দাও (bot admin হওয়ার পরে)।

Terminal/PC এ চালাও:

curl -s "https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates" | jq .


(Windows এ jq না থাকলে সাধারণ curl আউটপুট দেখো) — response-এ channel_post.chat.id পাবে = -100...
Important: bot টোকেন কখনো public repo-তে commit করবে না — Render ENV VAR এ রাখো। নিচে বলছি।

6) Bot token কোথায় রাখবে (security)

NEVER commit token to Git. Render এ Environment variable এ রাখো। Render → service → Environment → Add Environment Variable:

Name: BOT_TOKEN

Value: 8435...

কোডে os.getenv("BOT_TOKEN") দিয়ে access করো। (আমরা আগে code-এ এভাবে সেট করেছি)

7) ছোট-খাটো পরীক্ষা (Testing checklist) — প্রতিবার কনফিগ বদলালে করো

Commit & push → Render auto-deploy (বা Manual deploy).

Render → Service → Logs → live tail দেখো (Deploy success)।

Source channel-এ একটি ছোট টেস্ট পোস্ট দাও (টেক্সট)।

Logs-এ POST / বা Received update দেখো।

Target channel এ পোস্ট গেছে কি না চেক করো।

যদি না যায় → Logs copy করে এখানে পেস্ট করো, আমি দেখব।

8) কিভাবে rollback করো (কিছু ভুল হলে)

GitHub → <>Code → config.json → History → পুরোনো commit-এ ফিরে গিয়ে Revert করে দাও।

অথবা Git CLI দিয়ে:

git revert <commit_hash>
git push origin main


Render redeploy করে আগের কনফিগ হিসেবে ফিরে যাবে।

9) ভালো প্র্যাকটিস ও সতর্কতা (অবশ্যই রাখবেন)

Bot Token only Render env vars-এ রাখবে। Repo public হলে token কখনো রাখো না।

যখন নতুন target private channel যোগ করো → bot-কে admin করো; না হলে forward fail হবে।

অনেক চ্যানেলে একসাথে পোস্ট করলে Telegram rate-limit লাগতে পারে — পর্যাপ্ত বিলম্ব / retry রাখা ভালো।

Keywords লিখলে ছোট/বড় বর্ণ फर्कে না (current code lowercase করে চেক করে) — কিন্তু শব্দ-boundary প্রয়োজন হলে regex ব্যবহার করো।

বড় পরিবর্তন করার আগে staging branch + separate Render service বানালে নিরাপদ।

10) উদাহরণ — নতুন Category “pak” যোগ করা (step-by-step, copy-paste)

GitHub → repo → config.json → Edit:

"destination_channels": {
  "all": [ -1003172610238 ],
  "deshi": [],
  "indian": [],
  "japan": [],
  "pak": [-1009999999999]
},
"filters": {
  "deshi": ["বাংলা","deshi"],
  "indian": ["india","hindi"],
  "japan": ["japan"],
  "pak": ["pakistan","pk","lahore"]
}


Commit changes → Render auto-deploy।

Test: Source channel-এ পোস্ট — যদি টেক্সট-এ “pakistan” শব্দ থাকে তা “pak” রুটে যাবে।

11) যদি তুমি চাই — আমি তোমার জন্য প্রস্তুত ready-to-edit config.json ও change log template দিতে পারি

তাতে তুমি প্রতিটি কনফিগ পরিবর্তনের জন্য ছোট commit message লিখবে — পরে ট্রেস করা সহজ হবে। (আমি দিতে পারি; বললে ফাইল তৈরি করে দেব)

12) সংক্ষিপ্ত অনুশীলন (কাজটি করে দেখো)

তুমি এখনই একটি ছোট টেস্ট করো:

GitHub → config.json → filters.deshi-তে "চলচ্চিত্র" যোগ করো। Commit.

Render logs দেখো deploy success।

Source channel-এ পোস্ট লেখো: এই বাংলা চলচ্চিত্র ট্রেলার

দেখো Target channel-এ গেল কি না।
(এই ছোট টেস্ট দিয়ে তুমি পুরো ফ্লো বুঝে যাবে)
