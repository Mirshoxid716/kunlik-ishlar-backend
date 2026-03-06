from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Job, Worker, Application
from .serializers import JobSerializer, WorkerSerializer, ApplicationSerializer, UserSerializer
from bot_app.utils import send_to_telegram, edit_telegram_markup
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
import os

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_staff=True)
    serializer_class = UserSerializer
    authentication_classes = [] # Bypass Session Authentication for API requests
    permission_classes = []

    @action(detail=False, methods=['post'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            return Response({
                'username': user.username,
                'is_superuser': user.is_superuser
            })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all().order_by('-created_at')
    serializer_class = JobSerializer
    authentication_classes = []
    permission_classes = []

    @action(detail=True, methods=['post'])
    def notify_client(self, request, pk=None):
        job = self.get_object()
        apps = Application.objects.filter(job=job, status='approved')
        
        if not apps.exists():
            return Response({'error': 'Tasdiqlangan ishchilar mavjud emas'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Gather worker info
        workers_info = ""
        for i, app in enumerate(apps, 1):
            workers_info += f"{i}. {app.worker.full_name} - {app.worker.phone_number}\n"

        try:
            import html
            admin_id = os.getenv("ADMIN_ID", "5669525697")
            
            safe_title = html.escape(str(job.title))
            safe_unical = html.escape(str(job.unical_id))
            
            text = (
                f"<b>📊 ISH BO'YIChA YAKUNIY RO'YXAT</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                f"<b>💼 Ish:</b> {safe_title} (#{safe_unical})\n"
                f"<b>👥 Jami ishchilar:</b> {apps.count()}\n\n"
                f"<b>👤 Ishchilar ro'yxati:</b>\n{workers_info}\n"
                f"✅ Barcha ishchilar bilan bog'lanishingiz mumkin."
            )

            notify_sent = False

            if job.client_tg_username:
                client_username = job.client_tg_username.strip().replace('@', '')
                client_worker = Worker.objects.filter(username__iexact=client_username).first()
                if client_worker:
                    res = send_to_telegram(text, chat_id=client_worker.telegram_id)
                    if res and res.status_code == 200:
                        notify_sent = True
                        return Response({'status': 'sent_to_client'})
                    else:
                        print(f"Failed to send full list to client directly. Status: {res.status_code if res else 'None'}")
                
                if not notify_sent:
                    admin_alert = (
                        f"⚠️ <b>DIQQAT! KLIYENTGA XABAR BORMADI</b>\n\n"
                        f"Mijoz @{client_username} ga bot yakuniy ro'yxatni yetkazib bera olmadi (bot ochilmagan yoki o'chirilgan).\n"
                        f"Ro'yxatni unga qo'lda yuboring:\n\n{text}"
                    )
                    send_to_telegram(admin_alert, chat_id=admin_id)
                    return Response({'status': 'sent_to_admin_as_alert', 'message': 'Klient botda yo\'qligi sababli adminga yuborildi'})
            
            # Fallback to admin if no username
            send_to_telegram(text, chat_id=admin_id)
            return Response({'status': 'sent_to_admin'})
        except Exception as e:
            print(f"TELEGRAM ERROR in notify_client: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class WorkerViewSet(viewsets.ModelViewSet):
    queryset = Worker.objects.all()
    serializer_class = WorkerSerializer
    authentication_classes = []
    permission_classes = []

    def get_queryset(self):
        queryset = super().get_queryset()
        telegram_id = self.request.query_params.get('telegram_id')
        if telegram_id:
            queryset = queryset.filter(telegram_id=telegram_id)
        return queryset

class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all().order_by('-applied_at')
    serializer_class = ApplicationSerializer
    authentication_classes = []
    permission_classes = []

    def get_queryset(self):
        queryset = super().get_queryset()
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        return queryset

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        try:
            instance = self.get_object()
            instance.status = 'approved'
            instance.save()
            
            # Format location link if exists
            location_link = instance.job.address if instance.job.address else "Lokatsiya"
            if instance.job.location_url:
                location_link = f"<a href='{instance.job.location_url}'>{instance.job.address if instance.job.address else 'LOKATSIYANI KO\'RISH'}</a>"

            # Notify Worker (Try to notify, but don't crash if Telegram fails)
            try:
                full_text = (
                    f"✅ <b>Arizangiz tasdiqlandi!</b>\n\n"
                    f"📞 <b>Ish beruvchi raqami:</b> {instance.job.client_phone or 'Noma\'lum'}\n"
                    f"📍 <b>Manzil:</b> {location_link}\n"
                    f"💰 <b>Ish haqqi:</b> {instance.job.wage}\n"
                    f"🌟 <b>Xizmat haqi:</b> {int(instance.job.service_fee):,} so'm\n"
                    f"⏰ <b>Ish vaqti:</b> {instance.job.working_hours or 'Noma\'lum'}"
                )
                send_to_telegram(full_text, chat_id=instance.worker.telegram_id)
            except Exception as e:
                print(f"TELEGRAM ERROR during approval notify: {e}")

            # Notify Client & Admin (Try to notify)
            try:
                import html
                admin_id = os.getenv("ADMIN_ID", "5669525697")
                
                safe_title = html.escape(str(instance.job.title))
                safe_name = html.escape(str(instance.worker.full_name))
                safe_unical = html.escape(str(instance.job.unical_id))
                
                client_text = (
                    f"<b>🤝 ISHCHI TASDIQLANDI!</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"<b>💼 Ish:</b> {safe_title} (#{safe_unical})\n"
                    f"<b>👤 Ishchi:</b> {safe_name}\n"
                    f"<b>📞 Tel:</b> {instance.worker.phone_number}\n\n"
                    f"✅ Ishchi bilan bog'lanishingiz mumkin."
                )
                
                notify_sent = False
                if instance.job.client_tg_username:
                    client_username = instance.job.client_tg_username.strip().replace('@', '')
                    client_worker = Worker.objects.filter(username__iexact=client_username).first()
                    if client_worker:
                        res = send_to_telegram(client_text, chat_id=client_worker.telegram_id)
                        if res and res.status_code == 200:
                            notify_sent = True
                        else:
                            print(f"Failed to send to client directly. Status: {res.status_code if res else 'None'}")
                    
                    if not notify_sent:
                        admin_alert = (
                            f"⚠️ <b>DIQQAT! KLIYENTGA XABAR BORMADI</b>\n\n"
                            f"Mijoz @{client_username} ga bot ishchi haqidagi ma'lumotni yetkazib bera olmadi (yoki u botni o'chirgan, yoki botdan ro'yxatdan o'tmagan).\n"
                            f"Unga quyidagi ishchi ma'lumotlarini qo'lda yuboring:\n\n"
                            f"{client_text}"
                        )
                        send_to_telegram(admin_alert, chat_id=admin_id)
                        notify_sent = True
                
                if not notify_sent:
                    send_to_telegram(client_text, chat_id=admin_id)
            except Exception as e:
                print(f"TELEGRAM ERROR during client/admin notify: {e}")

            # Check Job Capacity
            job = instance.job
            approved_count = Application.objects.filter(job=job, status='approved').count()
            
            if approved_count >= job.required_workers:
                job.status = 'closed'
                job.save()
                
                if job.channel_post_id:
                    try:
                        from .utils import edit_telegram_markup
                        edit_telegram_markup(job.channel_post_id, reply_markup=None)
                    except Exception as e:
                        print(f"BOT ERROR during markup edit: {e}")
            
            return Response({'status': 'approved'}, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"CRITICAL ERROR in approve action: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        try:
            instance = self.get_object()
            reason = request.data.get('rejection_reason', 'Sabab ko\'rsatilmadi')
            instance.status = 'rejected'
            instance.rejection_reason = reason
            instance.save()
            
            try:
                reject_text = (
                    f"❌ <b>Sizning #{instance.job.unical_id} so'rovingiz rad etildi.</b>\n\n"
                    f"<b>Sabab:</b> {reason}\n\n"
                    f"Iltimos, adminga yozing yoki boshqa ishga urinib ko'ring."
                )
                send_to_telegram(reject_text, chat_id=instance.worker.telegram_id)
            except Exception as e:
                print(f"TELEGRAM ERROR during rejection notify: {e}")

            return Response({'status': 'rejected'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
