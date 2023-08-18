from django.shortcuts import render
from .models import MF,Investment
from django.contrib.auth.decorators import login_required
from datetime import datetime
@login_required(login_url='/account/login/')
def mf_home(request):
    pass


@login_required(login_url='/account/login/')
def investment_summary(request):
    inv_obj=Investment.objects.get(user=request.user,year=datetime.now().year)
    mf={'Name':'Mutual Funds','Amount':inv_obj.MF,'Invested':inv_obj.MF_i}
    smallcase={'Name':'SmallCase','Amount':inv_obj.SmallCase,'Invested':inv_obj.SmallCase_i}
    trade={'Name':'Trade','Amount':inv_obj.trade,'Invested':inv_obj.trade_i}
    large={'Name':'Large Cap Equity','Amount':inv_obj.large,'Invested':inv_obj.large_i}
    mid={'Name':'Mid Cap Equity','Amount':inv_obj.mid,'Invested':inv_obj.mid_i}
    small={'Name':'Small Cap Equity','Amount':inv_obj.small,'Invested':inv_obj.small_i}
    FD={'Name':'Fixed Deposits','Amount':inv_obj.FD,'Invested':inv_obj.FD_i}
    SGB={'Name':'Sovereign Gold Bonds','Amount':inv_obj.SGB,'Invested':inv_obj.SGB_i}
    inv_obj=[mf,smallcase,trade,large,mid,small,FD,SGB]
    return render(request, 'investment_summary.html',context={"inv":inv_obj})


@login_required(login_url='/account/login/')
def previous_investment(request):
    pass