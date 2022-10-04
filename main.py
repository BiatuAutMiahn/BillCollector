import tornado.ioloop
import tornado.web
import json
import time
import re
import csv
import datetime
from pyppeteer import launch
import asyncio
import pyppeteer

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('''
<html>
	<head>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.4.0/jquery.min.js"></script>
		<link href="https://fonts.googleapis.com/css?family=Inconsolata" rel="stylesheet">
        <style>
            html,body {
              font-family: 'Inconsolata', monospace;
              font-size: 14px;
              background: #2b2b2b;
              color: #3b3b3b;
              transition: all 0.5s ease;
            }
            * {
              box-sizing: border-box;
            }
            .container {
              width: 100%;
              max-width: 800px;
              margin: auto;
              padding: 8px 8px;
            }

            /* FLEX TABLE */
            .flex-table {
              width: 100%;
            }
            .flex-table [class^='flex-table--'] {
              display: flex;
              width: 100%;
            }
            .flex-table [class^='flex-table--']:not(.flex-table--body):not(.flex-table--header) {
              padding: 0.4em 0.2em;
            }
            .flex-table [class^='flex-table--'] span {
              display: block;
              flex: 1.5;
            }
            .flex-table [class^='flex-table--'] .num {
              display: block;
              flex: 1.5;
            }
            .flex-table [class^='flex-table--'] span:nth-child(1) {
              flex: inherit;
              margin-right: 8px;
            }
            .flex-table [class^='flex-table--'] .num:nth-child(1) {
              flex: inherit;
              margin-right: 8px;
            }
            .flex-table [class^='flex-table--'] span:nth-child(2) {
              flex: 3;
              max-width: 18em;
            }
            .flex-table [class^='flex-table--'] .num:nth-child(2) {
              flex: 3;
              max-width: 18em;
            }
            .flex-table .flex-table--header {
              background: #4965a7;
              color: #fff;
              //margin-bottom: 0.6em;
              box-shadow: 2px 2px 6px -2px rgba(34, 34, 34, 0.2);
              border-radius: 8px 8px 0 0;
            }
            .flex-table .flex-table--body {
              flex-direction: column;
              background: #f6f6f6;
              box-shadow: 5px 5px 10px -1px rgba(34, 34, 34, 1);
              border-radius: 0 0 8px 8px;
            }
            .flex-table .flex-table--row {
              position: relative;
              overflow:hidden;
            }
            .flex-table .flex-table--row:last-child {
              border-radius: 0 0 8px 8px;
            }
            .flex-table .flex-table--row:nth-child(even) {
              background: #e9e9e9;
            }
            .flex-table .flex-table--row:after {
              content: "";
              position: absolute;
              top: 50%;
              left: 0;
              background: #fff;
              height: 10px;
              width: 10px;
              -webkit-transform: translate(-50%, -50%);
                      transform: translate(-50%, -50%);
              border-radius: 50%;
              opacity: 0;
            }
            .hidden {
                height: 0em;
                padding: 0em 0.2em !important;
                -webkit-transition: height 0.5s ease,padding 0.5s ease !important;
                   -moz-transition: height 0.5s ease,padding 0.5s ease !important;
                    -ms-transition: height 0.5s ease,padding 0.5s ease !important;
                     -o-transition: height 0.5s ease,padding 0.5s ease !important;
                        transition: height 0.5s ease,padding 0.5s ease !important;
            }

            .hidden-open {
                 height: 2em;
                 padding: 0.4em 0.2em !important;
                 -webkit-transition: height 0.5s ease,padding 0.5s ease !important;
                    -moz-transition: height 0.5s ease,padding 0.5s ease !important;
                     -ms-transition: height 0.5s ease,padding 0.5s ease !important;
                      -o-transition: height 0.5s ease,padding 0.5s ease !important;
                         transition: height 0.5s ease,padding 0.5s ease !important;
            }

            .row-error{
            	background-color: #ffa8a8 !important;
            }

            .row-abtdue{
            	background-color: #ffd4a8 !important;
            }

            .row-disabled{
            	background-color: #909090 !important;
            }

            .row-due{
            	background-color: #ffd4a8 !important;
            }

            .span-num {
            	text-align: right;
            	max-width:4em;
            }

            #loader {
                overflow:hidden;
            }
            .loader-container {
              animation: rotate 1s linear infinite;
            }

            .loader-container .path {
              stroke: #000000;
              animation: dash 1.5s ease-in-out infinite;
            }

            @keyframes rotate {
              100% { transform: rotate(360deg); }
            }

            @keyframes dash {
              0% {
                stroke-dasharray: 1, 150;
                stroke-dashoffset: 0;
              }
              50% {
                stroke-dasharray: 90, 150;
                stroke-dashoffset: -35;
              }
              100% {
                stroke-dasharray: 90, 150;
                stroke-dashoffset: -124;
              }
            }
        </style>
        <script>
            var bills=null;
            var lastTime=null;
            var now = new Date();
            var loader=$('<div id="loader" class="flex-table--row"><span></span><svg class="loader-container" width="20px" height="20px" viewBox="0 0 52 52"><circle class="path" cx="26px" cy="26px" r="20px" fill="none" stroke-width="4px"></circle></svg></div>')
            var total=0;
            $(document).ready(function(){
                setInterval(function(){
                    jQuery.getJSON( "getbills", function( data ) {
                      lastTime=now.getTime()
                      bills=data;
                    ;});
                }, 125);
            });
            window.setInterval(function(){

                if ($('#bill-table').children().not($("#loader")).length>0){
                    $("#loader").removeClass("hidden").removeClass("hidden-open").addClass("hidden");
                    setTimeout(function(){
                        $("#loader").remove();
                    },500);
                } else {
                    var loader=$('<div id="loader" class="flex-table--row"><span></span><svg class="loader-container" width="20px" height="20px" viewBox="0 0 52 52"><circle class="path" cx="26px" cy="26px" r="20px" fill="none" stroke-width="4px"></circle></svg></div>')
                    loader.addClass("hidden")
                    $("#bill-table").append(loader)
                    setTimeout(function(){
                        $("#loader").removeClass("hidden").removeClass("hidden-open").addClass("hidden-open");
                    },500);
                }
                setTimeout(function(){
                    total=0;
                    $.each(bills,function(i,bill){
                    	var alias=bill['Alias'];
                    	var id=alias.toLowerCase().replace(/\ /g,'-');
                    	var status=bill['Status'];
                    	var statmsg=bill['StatusMsg'];
                    	if (statmsg==null){
                    		statmsg="Unknown Error";
                    	}
                        if (!$("#bill-table").has($("#"+id)).length){
                        	var rowelem=$('<div class="flex-table--row"><span></span></div>');
                        	var compelem=$("<span>"+alias+"</span>");
                        	var statelem=$('<span style="text-align: left"></span>');
                        	rowelem.attr('id',id);
                        	compelem.attr('id',id+"-company");
                        	statelem.attr('id',id+"-status");
                        	if (status!="Success"){
                        		rowelem.removeClass("row-error");
                        		rowelem.removeClass("row-disabled");
                        		if (status=="Error"){
                        			rowelem.addClass("row-error");
                        			statelem.text("Error: "+statmsg);
                        		} else if (status=="Disabled"){
                        			rowelem.addClass("row-disabled");
                        			statelem.text("Disabled");
                        		} else if (status=="Updating"){
                        			statelem.text("Updating: "+statmsg);
                        		}
                        	}
                        	rowelem.append(compelem);
                    		if (status=="Updating"){
                                var loader=$('<svg id="'+id+'-loader" style="margin-right:8px" class="loader-container" width="16px" height="16px" viewBox="0 0 52 52"><circle class="path" cx="26px" cy="26px" r="20px" fill="none" stroke-width="4px"></circle></svg>')
                                rowelem.append(loader)
                    		}
                        	rowelem.append(statelem);
                            rowelem.removeClass("hidden").removeClass("hidden-open").addClass("hidden")
                        	$("#bill-table").prepend(rowelem);
                            setTimeout(function(){
                                rowelem.removeClass("hidden").removeClass("hidden-open").addClass("hidden-open")
                            },i*500);
                        	console.log(bill);
                        } else {
                        	if (status!="Success"){
                                if ($("#bill-table").has($("#"+id+"-bal")).length){
                                    $("#"+id+"-bal").remove();
                                    $("#"+id+"-pdue").remove();
                                    $("#"+id+"-ddue").remove();
                                    var loader=$('<svg id="'+id+'-loader" style="margin-right:8px" class="loader-container" width="16px" height="16px" viewBox="0 0 52 52"><circle class="path" cx="26px" cy="26px" r="20px" fill="none" stroke-width="4px"></circle></svg>')
                                    $("#"+id).append(loader)
                        	        var statelem=$('<span style="text-align: left"></span>');
                                    statelem.attr('id',id+"-status");
                        	        $("#"+id).append(statelem);
                                }
                        		if (status=="Error"){
                                    if ($("#"+id).hasClass("row-disaled")) {$("#"+id).removeClass("row-disabled")};
                        			$("#"+id).addClass("row-error")
                        			$("#"+id+"-status").text("Error: "+statmsg);
                        		} else if (status=="Disabled"){
                                    if ($("#"+id).hasClass("row-error")) {$("#"+id).removeClass("row-error")};
                        			$("#"+id).addClass("row-disabled");
                        			$("#"+id+"-status").text("Disabled");
                        		} else if (status=="Updating"){
                                    if ($("#"+id).hasClass("row-error")) {$("#"+id).removeClass("row-error")};
                                    if ($("#"+id).hasClass("row-disaled")) {$("#"+id).removeClass("row-disabled")};
                        			$("#"+id+"-status").text("Updating: "+statmsg);
                        		}
                        	} else { // Success
                                $("#"+id+"-status").text("Success");
                                setTimeout(function(){
                                    $("#"+id+"-status").remove();
                                    $("#"+id+"-loader").remove();
                                    if (bill['Bill']['Balance']>0){
                                        total+=parseFloat(bill['Bill']['Balance'])
                                    }
                                    if (!$("#bill-table").has($("#"+id+"-bal")).length){
                                        var billelem=$('<span id="'+id+'-bal">'+bill['Bill']['Balance']+'</span><span id="'+id+'-pdue">'+bill['Bill']['PastDue']+'</span><span id="'+id+'-ddue">'+bill['Bill']['DateDue']+"</span>");
                                        $("#"+id).append(billelem);
                                        if (parseFloat($("#totaldue").text())!=total) {$("#totaldue").text(total.toFixed(2))};
                                    }
                                },500);
                            }
                        }
                    });

                },500);
            },50);
        </script>
	</head>
	<body>
		<div class="container">
			<div class="flex-table">
				<div class="flex-table--header">
					<div class="flex-table--categories"><span></span>
						<span>Company</span>
						<span>Current Balance</span>
						<span>Past Due</span>
						<span>Due Date</span>
					</div>
				</div>
				<div id="bill-table" class="flex-table--body">
					<div id="loader" class="flex-table--row"><span></span>
                        <svg class="loader-container" width="20px" height="20px" viewBox="0 0 52 52">
                          <circle class="path" cx="26px" cy="26px" r="20px" fill="none" stroke-width="4px"></circle>
                        </svg>
					</div>
				</div>
			</div>
		</div>
		<div class="container">
			<div class="flex-table">
				<div class="flex-table--header">
					<div class="flex-table--categories"><span></span>
						<span>Total Due</span>
					</div>
				</div>
				<div class="flex-table--body">
					<div class="flex-table--row"><span></span>
						<span id="totaldue">0.00</span>
					</div>
				</div>
			</div>
		</div>
	</body>
</html>
''')

bills=[{
    "Disable": True,
    "Alias": "Progressive Auto Insurance",
    "Tasks": [
        {"Nav": "https://account.progressive.com/access/login?cntgrp=Q&session_start=true"},
        {"Login": {
            "Selector": {"User": "input[data-pgr-id='inputUserName']","Pass": "input[data-pgr-id='inputPassword']","Login": "button[data-pgr-id='buttonSubmitLogin']"},
            "User": "B************",
            "Pass": "B***************"
        }},
        {"Click": ".lastPaymentReceived"},
        {"Await": "#console"},
        {"EvalJsBrute": '''() => {var eval=$("#console:contains('Remaining balance') tr").map(function() {return [$(this).find('td').map(function() {return $(this).text().trim()}).get()]}).get();delete eval[0];eval=JSON.stringify(eval.filter(function(x){return x!==null}));return eval}'''},
        {"EvalPy": '''eval=json.loads(eval)\neval={'Balance':eval[2][1].replace('$',''),'PastDue':eval[1][2].replace('$',''),'DateDue':datetime.datetime.strptime(eval[1][1],'%m/%d/%Y').strftime("%Y.%m.%d")}'''},
    ],},{
    "Disable": True,
    "Alias": "Piedmont Natural Gas",
    "Tasks": [
        {"Nav": "https://www.piedmontng.com/youraccount/onlineservices/billinformation.aspx"},
        {"Login": {
            "Selector": {"User": "#ctl00_BodyCopy_Login1_LoginView1_Login1_UserName","Pass": "#ctl00_BodyCopy_Login1_LoginView1_Login1_Password","Login": "#ctl00_BodyCopy_Login1_LoginView1_Login1_BtnLogin"},
            "User": "B************",
            "Pass": "s***************"
        }},
        {"Await": "#ctl00_BodyCopy_BillingInformationForm1_lblYesterday"},
        {"EvalJs": '''() => {var t=document.getElementById("ctl00_BodyCopy_BillingInformationForm1_lblYesterday").parentElement.parentElement.parentElement;return bal=$(t).find('td:contains("Account Balance as of")').next("td").text(),datedue=$(t).find('td:contains("Current Charges Past Due After")').next("td").text().replace(/(\d{2})\/(\d{2})\/(\d{4})/g,'$3.$1.$2'),pastdue=$(t).find('td:contains("Total Past Due Balance")').next("td").text(),{DueDate:datedue,CurrentBalance:bal,PastBalance:pastdue}}'''},
        {'EvalPy': '''eval={'Balance':eval['CurrentBalance'].replace('$',''),'PastDue':eval['PastBalance'].replace('$',''),'DateDue':eval['DueDate']}'''}
    ],},{
    "Disable": False,
    "Alias": "Magnolia Rental Property Management",
    "Tasks": [
        {"Nav": "https://secure.rentecdirect.com/tenants/t/tstatement.php"},
        {"Login": {
            "Selector": {"User": "#username","Pass": "#password","Login": "#Login"},
            "User": "B************",
            "Pass": "H*******"
        }},
        {"Nav": "https://secure.rentecdirect.com/tenants/t/tstatement.php"},
        {"EvalJs": '''() => {var e = null;$.ajax({url: "tcsv_download.php?date_begin=2019-01-01&date_end=2019-04-30",type: "get",dataType: "html",async: 0,cache: 0,success: function(a) {e = a;}});return e;}'''},
        {"EvalPy": '''def read_csv(dat):\n\tcsv_rows = []\n\treader = csv.DictReader(dat.splitlines())\n\ttitle = reader.fieldnames\n\tfor row in reader:\n\t\tcsv_rows.extend([{title[i]:row[title[i]] for i in range(len(title))}])\n\treturn csv_rows[-1]\n
eval=read_csv(eval)\neval={'Balance':format(-int(eval['Balance']),'.2f'),'PastDue':format(-int(eval['Balance']),'.2f'),'DateDue':datetime.datetime.strptime(eval['Date'],'%m/%d/%Y').strftime("%Y.%m.01")}'''}
    ],},{
    "Disable": False,
    "Alias": "Duke Energy",
    "Tasks": [
        {"Nav": "https://duke-energy.mypaygo.com/Portal/SSL/CUST/CUST_Login.aspx"},
        {"Login": {
            "Selector": {"User": "#txtAcct","Pass": "#txtPassword","Login": "#cmdSubmit"},
            "User": "C*******************************",
            "Pass": "8***************"
        }},
        {"Await": "#ctl00_ContentPlaceHolder1_lblAsOf"},
        {"EvalJs": '''() => {var a=$("#ctl00_ContentPlaceHolder1_lblAsOf");if (!a.length) {a=null}else{a=a.text()};var b=$("#ctl00_ContentPlaceHolder1_lblApproxDollars");if (!b.length) {a=null}else{b=b.text()};var c=$("#ctl00_ContentPlaceHolder1_lblDeferredBalance");if (!c.length) {a=null}else{c=c.text()};var d=$("#ctl00_ContentPlaceHolder1_lblApproxDaysLabel");if (!d.length) {a=null}else{d=d.text()};var e=$("#ctl00_ContentPlaceHolder1_lblApproxDailyDollar");if (!e.length) {a=null}else{e=e.text()};var f=$("#ctl00_ContentPlaceHolder1_lblAverageDailyConsumption");if (!f.length) {a=null}else{f=f.text()};return {AsOf:a,ApproxDollars:b,DeferredBalance:c,ApproxDays:d,ApproxDailyDollar:e,AverageDailyConsumption:f}}'''},
        {"EvalPy": '''if re.match("\(\$([\d.]*)\)",eval['ApproxDollars']):\n\teval['ApproxDollars']=format(-float(re.findall("\(\$([\d.]*)\)",eval['ApproxDollars'])[0]),".2f")\n\teval['DeferredBalance']=format(-float(eval['ApproxDollars']),".2f")\neval={'Balance': format(-float(eval['ApproxDollars'].replace('$','')),'.2f'),'PastDue':eval['DeferredBalance'].replace('$',''),'DateDue':(datetime.datetime.strptime(eval['AsOf'], '%m/%d/%Y %I:%M:%S %p')+datetime.timedelta(days=int(eval['ApproxDays']))).strftime("%Y.%m.%d")}'''},
    ],},{
    "Disable": False,
    "Alias": "Spartanburg Water",
    "Tasks": [
        {"Nav": "https://link.sws-sssd.org/Home.aspx"},
        {"Login": {
            "Selector": {"User": "#dnn_ctr1216_Login_Login_DNN_txtUsername","Pass": "#dnn_ctr1216_Login_Login_DNN_txtPassword","Login": "#dnn_ctr1216_Login_Login_DNN_cmdLogin"},
            "User": "B************",
            "Pass": "s***************"
        }},
        {"Await": "#dnn_ctr1267_BillingHistory_GridView1"},
        {"EvalJs": '''() => {var eval=$("#dnn_ctr1267_BillingHistory_GridView1 tr").map(function() {return [$(this).find('td').map(function() {return $(this).text().trim()}).get()]}).get();delete eval[0];eval=eval.filter(function(x){return x!==null});eval=eval[0];eval.push(String($('#dnn_INFOPOPUP1_lblDueDate').text()));return JSON.stringify(eval)}'''},
        {"EvalPy": '''eval=json.loads(eval)\neval={'Balance':format(float(eval[4].replace('$','')),'.2f'),'PastDue':format(float(eval[2].replace('$','')),'.2f'),'DateDue':datetime.datetime.strptime(eval[6],'Due Date : %m/%d/%Y').strftime("%Y.%m.%d")}'''},
    ],},{
    "Disable": False,
    "Alias": "Spectrum",
    "Tasks": [
        {"Nav": "https://www.spectrum.net/login/?targetUrl=https:%2F%2Fwww.spectrum.net%2Fbilling-and-transactions"},
        {"Login": {
            "Selector": {"User": "#cc-username ","Pass": "#cc-user-password","Login": "#login-form-button"},
            "User": "B************",
            "Pass": "s***************"
        }},
        {"Await": ".bill-pay-content-wrapper-sm"},
        {"EvalJs": '''() => {var bal=$("spectrum-card-title span:contains('Amount Due')").next().text().replace(/\ /g,'');var ddate=$("spectrum-card-content-section span:contains('Payment Due By')").next().text();return {Balance:bal,PastDue:"0.00",DateDue:ddate}}'''},
        {"EvalPy": '''print(eval)\neval={'Balance':format(float(eval['Balance'].replace('$','')),'.2f'),'PastDue':format(float(eval['PastDue'].replace('$','')),'.2f'),'DateDue':datetime.datetime.strptime(eval['DateDue'],'%m/%d/%y').strftime("%Y.%m.%d")}'''},
    ]}
]

billreq=[]
browser = None

class BillHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(json.dumps(billreq,indent=2));

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),(r"/getbills", BillHandler),
    ])

async def AwaitSelector(page,selector: str):
    retry=0
    while True:
        try:
            test=await page.waitForSelector(selector,{'timeout': 1000,'visible':True})
            # print('AwaitSelector('+selector+')')
            # print(dir(test))
            # print(test)
            # import code;code.InteractiveConsole(locals=dict(globals(), **locals())).interact()
        except pyppeteer.errors.TimeoutError:
            retry=1
            if retry==30:
                raise Exception('Unable to await selector!')
            continue
        break
    #await page.waitForNavigation({'waitUntil':'networkidle2'})



async def procbillreq():
    # print("pass")

    for b in bills:
        def doCheck():
            if len(billreq)>0:
                for d in billreq:
                    if 'Alias' in d:
                        if d['Alias']==b['Alias']:
                            return True
            return False
        if doCheck():
            continue
        if 'Disable' in b:
            if b['Disable']:
                bill={"Alias": b["Alias"],"LastUpdate": int(round(time.time() * 1000)), "Status": "Disabled", "StatusMsg": None, "Bill": None}
                billreq.append(bill)
                continue
        bill={"Alias": b["Alias"],"LastUpdate": int(round(time.time() * 1000)), "Status": "Updating", "StatusMsg": "Initializing...", "Bill": None}
        billreq.append(bill)

async def update_billreq():
    while True:
        await procbillreq()
        await tornado.gen.sleep(0.25)

async def getBill(browser,d):
    brq=None
    if len(billreq)>0:
        for b in billreq:
            if 'Alias' in b:
                if d['Alias']==b['Alias']:
                    brq=b
    # print("Retriving "+d['Alias']+' bill')
    brq['Status']="Updating"
    page=await browser.newPage()
    eval=None
    for task in d['Tasks']:
        action=list(task.keys())[0]
        if action=="Nav":
            brq['StatusMsg']="Navigating..."
            await asyncio.wait([
                page.goto(task.get(action)),
                page.waitForNavigation(),
                page.addScriptTag({'url': 'https://code.jquery.com/jquery-latest.min.js'}),
            ])
        elif action=="Click":
            await AwaitSelector(page,task.get(action))
            brq['StatusMsg']="Interacting..."
            await asyncio.gather(
                page.waitForNavigation(),
                page.click(task.get(action)),
            )
        elif action=="Await":
            brq['StatusMsg']="Waiting..."
            await AwaitSelector(page,task.get(action))
        elif action=="Login":
            await AwaitSelector(page,task.get(action)['Selector']['User'])
            await page.type(task.get(action)['Selector']['User'],task.get('Login')['User'])
            await AwaitSelector(page,task.get(action)['Selector']['Pass'])
            await page.type(task.get(action)['Selector']['Pass'],task.get('Login')['Pass'])
            await AwaitSelector(page,task.get('Login')['Selector']['Login'])
            brq['StatusMsg']="Logging in..."
            await asyncio.gather(
                page.waitForNavigation(),
                page.click(task.get(action)['Selector']['Login']),
            )
        elif action=="EvalJs":
            brq['StatusMsg']="Processing..."
            await page.addScriptTag({'url': 'https://code.jquery.com/jquery-latest.min.js'}),
            eval=await page.evaluate(task.get(action))
            # import code;code.InteractiveConsole(locals=dict(globals(), **locals())).interact()
            # await asyncio.sleep(0.1)
        elif action=="EvalJsBrute":
            brq['StatusMsg']="Processing..."
            while True:
                eval=await page.evaluate(task.get(action))
                # await asyncio.sleep(0.1)
                if not (eval=='[]' or eval=='{}' or eval is None or eval is None):
                    break
        elif action=="Wait":
            brq['StatusMsg']="Waiting..."
            await page.waitFor(task.get(action))
        elif action=="EvalPy":
            brq['StatusMsg']="Processing..."
            ldic=locals()
            exec(task.get(action),globals(),ldic)
            eval=ldic["eval"]
        await asyncio.sleep(0.5)
    brq['Status']="Success"
    brq['StatusMsg']=None
    brq['LastUpdate']=int(round(time.time() * 1000))
    brq['Bill']=eval
    await page._client.send('Network.clearBrowserCookies');
    await page.close()


async def update_bills():
    browser = await launch(headless=True,args={"--disable-infobars"})
    while True:
        await tornado.gen.sleep(10)
        for b in bills:
            if 'Disable' in b:
                if b['Disable']:
                    continue
            tornado.ioloop.IOLoop.current().spawn_callback(getBill,browser,b)
        await tornado.gen.sleep(300)

if __name__ == "__main__":

    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().spawn_callback(update_billreq)
    tornado.ioloop.IOLoop.current().spawn_callback(update_bills)
    tornado.ioloop.IOLoop.current().start()
