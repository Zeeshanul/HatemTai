from django.http import HttpResponse
from django.views import View
from django.contrib.auth import views as auth_view
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import auth
from .forms import UserForm as UserForm
from django.contrib import messages
from .models import User as User, Stocks as Stocks, ForexData, Event
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from forex_python.converter import CurrencyRates
import io
import csv

from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode


class Index(View):
    def get(self, request):
        # <view logic>
        try:
            forex = ForexData.objects.all()
            return render(request, 'index.html', {'user': request.user, 'forex': forex})
        except Exception as e:
            return redirect('/')


class MarketSummary(View):
    def get(self, request):
        # <view logic>
        try:
            user = request.user
            return render(request, 'components-calendar.html', {'user': user})
        except Exception as e:
            return redirect('/')


class Login(View):
    def get(self, request):
        # <view logic>
        try:
            return render(request, 'signin.html', {})
        except Exception as e:
            return redirect('/')

    def post(self, request):
        user_name = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(username=user_name, password=password)
        if user:
            current_user = User.objects.get(username=user_name)
            if not current_user.is_active:
                messages.error(request, "Account is not Activated. Please activate your account first")
                return redirect('/accounts/login')
            auth.login(request, user)
            return redirect('/')
        else:
            messages.error(request, "Either email or password is incorrect")
            return redirect('/accounts/login')


class Logout(View):
    def get(self, request):
        # <view logic>
        try:
            auth.logout(request)
            return render(request, 'index.html', {})
        except Exception as e:
            return redirect('/')


class Register(View):
    def get(self, request):
        # <view logic>
        try:
            return render(request, 'register.html', {})
        except Exception as e:
            return redirect('/')

    def post(self, request):
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()
            email_id = request.POST.get('username')
            password = request.POST.get('password')
            if email_id and password:
                _user = User.objects.get(username=email_id)
                _user.email = email_id
                _user.set_password(password)
                _user.save()

                # region activation email
                _user.is_active = False
                _user.save()
                current_site = get_current_site(request)
                mail_subject = 'Activate your account.'
                message = render_to_string('acc_active_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                })
                to_email = _user.email
                email = EmailMessage(
                    mail_subject, message, to=[to_email]
                )
                email.send()
                # # endregion
            login(request, user)
            return HttpResponse('Registration has been successful. We have sent an activation link to'
                                ' your registered email address. Kindly activate your account by clicking on the link')
            # messages.success(request, "Registration successful. Please login with your credentials")
            # return redirect("/accounts/login/")
        messages.error(request, "User already exists. Please try with another email address")
        return redirect("/register")


@method_decorator(csrf_exempt, name='dispatch')
class StocksDetail(View):
    def post(self, request):
        try:
            event_id = request.POST.get('event_id')
            if event_id:
                data = {}
                if Stocks.objects.filter(event_id_id=event_id).exists():
                    stocks_detail = Stocks.objects.get(event_id_id=event_id)
                    data['script_name'] = stocks_detail.script_name
                    data['target_price'] = stocks_detail.target_price
                    data['stop_loss'] = stocks_detail.stop_loss
                    data['holding_period'] = stocks_detail.holding_period
                return JsonResponse({'status': 200, 'data': data})
        except Exception as e:
            return JsonResponse({'status': 400})
 

class StocksData(View):
    def post(self, request):
        try:
            script_name = request.POST.get('script_name')
            target_price = request.POST.get('target_price')
            stop_loss = request.POST.get('stop_loss')
            holding_period = request.POST.get('holding_period')
            user_id = request.user
            event_id = request.POST.get('event_id')
            if Stocks.objects.filter(event_id_id=event_id).exists():
                stock_data = Stocks.objects.get(user_id=user_id, event_id_id=event_id)
                stock_data.script_name = script_name
                stock_data.target_price = target_price
                stock_data.stop_loss = stop_loss
                stock_data.holding_period = holding_period
                stock_data.created_date = datetime.now()
                stock_data.save()

            else:
                stock_detail = Stocks(script_name=script_name, target_price=target_price, stop_loss=stop_loss,
                                      holding_period=holding_period, created_date=datetime.now(), user_id=user_id,
                                      event_id_id=event_id)
                stock_detail.save()
            messages.success(request, "Stock has been updated successfully")
            return redirect('/market_summary/')
        except Exception as e:
            messages.error(request, "Failed to create stock, please try again")
            return redirect('/market_summary/')


class Users(View):
    def get(self, request):
        # <view logic>
        try:
            users = User.objects.filter(is_superuser=False).order_by('id')
            return render(request, 'users.html', {'users': users})
        except Exception as e:
            return redirect('/')
    def post(self, request):
        try:
            user_id = request.POST.get('user_id')
            if user_id:
                user = User.objects.get(id=user_id)
                if user.role == 'User':
                    user.role = 'Admin'
                else:
                    user.role = 'User'
                user.save()
            return redirect('/users/')
        except Exception as e:
            return redirect('/')


class HitForexApi(View):
    def get(self, request):
        c = CurrencyRates()
        rates = c.get_rates('GBP')
        for code, price in rates.items():
            print('code:', code)
            print('value: ', price)
        return JsonResponse({'success': True})

    def post(self):
        pass


class ForexFileUpload(View):
    def get(self, request):
        forex = ForexData.objects.all()
        return render(request, 'forex_data.html', {"forex": forex})

    def post(self, request):
        try:
            csv_file = request.FILES['forexFile']
            data_set = csv_file.read().decode('latin-1')
            io_string = io.StringIO(data_set)
            next(io_string)
            for column in csv.reader(io_string, delimiter=',', quotechar="|"):
                currency_code = column[0]
                currency_new_value = column[1]
                if currency_new_value and currency_code:
                    arrow_direction = 'UP'
                    if ForexData.objects.filter(currency_code=currency_code).exists():
                        forex = ForexData.objects.get(currency_code=currency_code)
                        currency_old_value = forex.currency_value
                        if float(currency_new_value) < float(currency_old_value):
                            arrow_direction = 'DOWN'
                        else:
                            arrow_direction = forex.currency_arrow
                        forex.currency_arrow = arrow_direction
                        forex.currency_value = currency_new_value
                        forex.save()
                    else:
                        forex_data = ForexData(currency_code=currency_code, currency_value=currency_new_value,
                                                currency_arrow='UP', user_id=request.user)
                        forex_data.save()
            messages.success(request, "Forex Data Updated Successfully")
            return redirect('/forex_file_upload/')
        except Exception as e:
            messages.error(request, "File Upload Failed")
            return redirect('/forex_file_upload/')


class AddEvents(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(AddEvents, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        title = request.POST.get('title')
        start = request.POST.get('start')
        start = datetime.strptime(start.split('GMT')[0].strip(), "%a %b %d %Y %H:%M:%S")
        end = request.POST.get('end')
        end = datetime.strptime(end.split('GMT')[0].strip(), "%a %b %d %Y %H:%M:%S")
        event = Event(event_title=title, start_date=start, end_date=end)
        event.save()
        event_id = event.event_id
        all_events = list(Event.objects.all().order_by('event_id').values())
        return JsonResponse({'data': all_events, 'event_id': event_id, 'success': True, 'status': 200})

    def get(self, request):
        all_events = list(Event.objects.all().order_by('event_id').values())
        return JsonResponse({'data': all_events, 'success': True, 'status': 200})


def process_date(date):
    date_splited = date.split('GMT')[0]
    cleaned_date = date_splited.replace('00:00:00', '').strip()
    date = datetime.strptime(cleaned_date, "%a %b %d %Y")
    return date


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None:
        user.is_active = True
        user.save()
        messages.success(request, "Your account has been Activated successfully. Please login with your credentials")
        return redirect('/accounts/login')
    else:
        return HttpResponse('Activation link is invalid!')