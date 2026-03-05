import json
import os
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Job, Application
from bot_app.utils import send_to_telegram

@receiver(post_save, sender=Job)
def notify_new_job(sender, instance, created, **kwargs):
    print(f"DEBUG: notify_new_job signal fired. Created: {created}")
    if created:
        import html
        # Format Address with Link if location_url exists
        location_text = instance.address if instance.address else "Lokatsiya orqali"
        if instance.location_url:
            safe_url = html.escape(instance.location_url, quote=True)
            safe_address = html.escape(instance.address) if instance.address else "LOKATSIYANI KO'RISH"
            location_text = f'<a href="{safe_url}">{safe_address}</a>'

        # Beautiful design for Telegram Channel
        text = (
            f"<b>📢 YANGI ISH E'LONI</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>💼 Ish:</b> {instance.title}\n"
            f"<b>👥 Kerak:</b> {instance.required_workers} kishi\n"
            f"<b>💵 Maosh:</b> {instance.wage}\n"
            f"<b>🕒 Vaqt:</b> {instance.working_hours}\n"
            f"<b>📍 Manzil:</b> {location_text}\n"
            f"<b>💰 Xizmat haqi:</b> {int(instance.service_fee):,} so'm\n"
            f"<b>🔑 ID:</b> <code>#{instance.unical_id}</code>\n\n"
            f"<b>📝 Batafsil:</b>\n<i>{instance.description or 'Izoh yo\'q'}</i>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"✅ <b>Ishga yozilish uchun botga kiring:</b>"
        )
        
        reply_markup = {
            "inline_keyboard": [[
                {"text": "💼 ISHGA YOZILISH", "url": f"https://t.me/ish_flow_bot?start=apply_{instance.unical_id}"}
            ]]
        }
        
        try:
            response = send_to_telegram(text, reply_markup=json.dumps(reply_markup))
            if response is not None and response.status_code == 200:
                res_data = response.json()
                if res_data.get('ok'):
                    message_id = res_data['result']['message_id']
                    # Use update to avoid triggering signal again
                    Job.objects.filter(pk=instance.pk).update(channel_post_id=message_id)
            else:
                error_body = response.text if response is not None else "Text was blank (None)"
                print(f"TELEGRAM ERROR: {error_body}")
                Job.objects.filter(pk=instance.pk).update(description=f"{instance.description or ''}\n\n[ADMIN_XATOLIK: {error_body}]")
        except Exception as e:
            print(f"SIGNAL EXCEPTION (notify_new_job): {e}")
            Job.objects.filter(pk=instance.pk).update(description=f"{instance.description or ''}\n\n[ADMIN_XATOLIK: {str(e)}]")

@receiver(post_save, sender=Application)
def handle_application_saved(sender, instance, created, **kwargs):
    # 1. Notify Admin about new application
    # Trigger when status becomes 'pending' (meaning receipt was uploaded)
    if instance.status == 'pending':
        try:
            admin_id = os.getenv("ADMIN_ID")
            if admin_id:
                text = (
                    f"<b>🆕 YANGI ARIZA KELDI!</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"<b>👤 Ishchi:</b> {instance.worker.full_name}\n"
                    f"<b>📞 Tel:</b> {instance.worker.phone_number}\n"
                    f"<b>💼 Ish:</b> {instance.job.title} (#{instance.job.unical_id})\n"
                    f"<b>💰 Xizmat haqi:</b> {int(instance.job.service_fee):,} so'm\n\n"
                    f"✅ <i>Iltimos, admin paneldan to'lovni tekshiring va tasdiqlang.</i>"
                )
                send_to_telegram(text, chat_id=admin_id)
        except Exception as e:
            print(f"SIGNAL ERROR (admin notify): {e}")

    # 2. Manage Channel Button Visibility
    try:
        job = instance.job
        # Count of active applications (anyone taking a spot)
        active_apps = Application.objects.filter(job=job).exclude(status='rejected').count()
        
        from bot_app.utils import edit_telegram_markup, send_to_telegram
        
        if active_apps >= job.required_workers:
            if job.channel_post_id and job.status == 'open':
                # Remove the button from the channel post
                try:
                    edit_telegram_markup(job.channel_post_id, reply_markup=json.dumps({"inline_keyboard": []}))
                except: pass
                # Update status to closed
                Job.objects.filter(pk=job.pk).update(status='closed')
        else:
            # If active apps drop below required (e.g. rejection or timeout)
            if job.channel_post_id and job.status == 'closed':
                # Restore the button
                reply_markup = {
                    "inline_keyboard": [[
                        {"text": "💼 ISHGA YOZILISH", "url": f"https://t.me/ish_flow_bot?start=apply_{job.unical_id}"}
                    ]]
                }
                try:
                    edit_telegram_markup(job.channel_post_id, reply_markup=json.dumps(reply_markup))
                except: pass
                # Update status back to open
                Job.objects.filter(pk=job.pk).update(status='open')
                # Notify channel that a spot opened up
                opened_text = (
                    f"<b>🔄 BO'SH ISH O'RNI OCHILDI!</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"<b>💼 Ish:</b> {job.title} (#{job.unical_id})\n"
                    f"⚠️ <i>Spot bo'shadi, yozilishga shoshiling!</i>"
                )
                try:
                    send_to_telegram(opened_text)
                except: pass
    except Exception as e:
        print(f"SIGNAL ERROR (channel manage): {e}")



