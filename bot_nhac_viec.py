import requests
from supabase import create_client, Client
from datetime import datetime, timezone, timedelta

# ==========================================
# CONFIG
# ==========================================
SUPABASE_URL = "https://eqrfcbsiwqyplqrdstub.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVxcmZjYnNpd3F5cGxxcmRzdHViIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjE1MzQ0MSwiZXhwIjoyMDgxNzI5NDQxfQ.I6Qw4VXmG_u4asGCrL8SIWDIj9NybsxyIbSGRmoYGJk"

TELEGRAM_BOT_TOKEN = "7785342410:AAHcdXRCu6qZs-M4mGowF-65AAGzc1kdXjw"
TELEGRAM_GROUP_ID = "-5283852302"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def chay_bot_quet_du_lieu():

    print("🤖 Bot đang quét các Issue chưa xử lý...")

    res = supabase.table("crm_issues") \
        .select("*") \
        .in_("status", ["Open", "In Progress"]) \
        .execute()

    issues = res.data

    now = datetime.now(timezone.utc)

    count_canh_bao = 0

    for issue in issues:

        last_updated_str = issue.get("last_updated")
        last_reminded_str = issue.get("last_reminded")

        if not last_updated_str:
            continue

        try:

            last_updated = datetime.fromisoformat(
                last_updated_str.replace("Z", "+00:00")
            )

            # Nếu chưa từng remind
            if last_reminded_str:
                last_reminded = datetime.fromisoformat(
                    last_reminded_str.replace("Z", "+00:00")
                )
                moc_tinh = max(last_updated, last_reminded)
            else:
                moc_tinh = last_updated

            thoi_gian_tre = now - moc_tinh

            # ==========================
            # QUÁ 24H → REMIND
            # ==========================
            if thoi_gian_tre > timedelta(hours=24):

                so_gio_tre = int(thoi_gian_tre.total_seconds() // 3600)

                msg = (
                    f"🚨 <b>CẢNH BÁO: ISSUE KHÔNG UPDATE > 24H</b>\n\n"
                    f"📝 <b>Vấn đề:</b> {issue.get('description')}\n"
                    f"👤 <b>Người phụ trách:</b> {issue.get('assignee')}\n"
                    f"🏢 <b>Khách hàng:</b> {issue.get('customer_name')}\n"
                    f"⏳ <b>Đã treo:</b> {so_gio_tre} giờ\n\n"
                    f"<i>👉 Yêu cầu PIC vào CRM update ngay.</i>"
                )

                url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

                requests.post(
                    url,
                    json={
                        "chat_id": TELEGRAM_GROUP_ID,
                        "text": msg,
                        "parse_mode": "HTML"
                    }
                )

                # ==========================
                # LƯU LẠI THỜI GIAN REMIND
                # ==========================
                supabase.table("crm_issues").update({
                    "last_reminded": now.isoformat()
                }).eq("id", issue["id"]).execute()

                count_canh_bao += 1

        except Exception as e:
            print(f"Lỗi khi xử lý issue {issue.get('id')}: {e}")

    print(f"✅ Quét xong! Đã gửi {count_canh_bao} cảnh báo.")


if __name__ == "__main__":
    chay_bot_quet_du_lieu()
