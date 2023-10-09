import datetime

from django.shortcuts import render
from django.utils.timezone import get_current_timezone
from .models import PulseOutput, Pulse
from dateutil.relativedelta import relativedelta

# Create your views here.
from django.http import HttpResponse, JsonResponse


def index(request):
    return JsonResponse({'foo': 'bar'})


def list_pulse_outputs(request):
    response = JsonResponse(list(PulseOutput.objects.values()), safe=False)
    return response


def list_pulses(request):
    # Check parameters
    date_format = '%Y-%m-%d'
    tz = get_current_timezone()
    from_date_default = datetime.datetime.today() - relativedelta(months=1)
    to_date_default = datetime.datetime.today() + relativedelta(days=1)
    from_date = datetime.datetime.strptime(request.GET.get("from", from_date_default.strftime(date_format)),
                                           date_format).replace(tzinfo=tz)
    to_date = datetime.datetime.strptime(request.GET.get("to", to_date_default.strftime(date_format)),
                                         date_format).replace(tzinfo=tz)
    qry = Pulse.objects.filter(created__range=(from_date, to_date)).order_by('created')
    response = JsonResponse(list(qry.values('created', 'pulse_output')), safe=False)
    return response
