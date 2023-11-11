import logging

import azure.functions as func
from langchain.chat_models import ChatOpenAI
from langchain import PromptTemplate

from langchain.prompts import (
    ChatPromptTemplate,
    PromptTemplate,
    SystemMessagePromptTemplate,
)
import os
import json
import time
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
import pandas as pd
import io
load_dotenv()

template = '''
System: As your AI assistant, my purpose is to assist you in extracting information from invoices and provide the details in JSON format. Here's how it works:

Example 1:
input_invoice: {input}
output_json : {output}


input : {input_invoice}
output:
'''
template_1 = '''
System: You are an AI assistant. You will be given the definition of an evaluation metric for assessing the quality of an answer in a attribute-answer task. Your job is to compute an accurate evaluation score using the provided evaluation metric.

User:
Relevance measures how well the answer addresses the main aspects of the attribute, based on the context. Consider whether all and only the important aspects are contained in the answer when evaluating relevance. Given the context and question, score the relevance of the answer between zero to one using the following rating scale:
Zero stars : the answer is wrong or incomplete
One stars : the answer is completely correct

This rating value should always be an integer between 0 and 1. So the rating produced should be 0 or 1

Example 1:

context: Taswarer\nTasmanian Water and Sewerage Corporation Pty Ltd ABN 47 162 220 653\nCommunity Housing Limited Att: Accounts Payable 19-23 Prospect Street BOX HILL VIC 3128\nTax invoice summary\nBilling period 01 Jul 2023 - 30 Sep 2023\nFixed charges\n$2,813.96\nVariable usage charges\n$192.14\nGST\n$0.00\nTotal new charges (this bill)\n$3,006.10\nPrevious bill\n$2,896.31\nAdjustments\n-$2,896.31\nTotal\n$3,006.10\nYour current average use is 1.95 kL/day Your current average cost is $2.21/day\nMeter reading Your water usage for this quarter is based on a meter reading\n--- * If you plan to pay in person please do not cut\nTaswarer Payment slip\nAccount no.\n240040372\nConnection address 9 Hawkins Street LATROBE TAS\nDIRECT DEBIT\nDirect Debit\nBPAY BPAY®\nWould you like to receive all TasWater notices digitally? Scan this QR code, or visit: www.taswater.com.au/digital-billing\nPlease phone 13 6992 or visit\nwww.taswater.com.au/payment\nBiller code: 117309\nRef: 3991 2400 4037 22\nAll enquiries & emergencies 13 6992\nemail enquiries@taswater.com.au website www.taswater.com.au post GPO Box 1393 Hobart Tasmania 7001\nf\nTasWater1 Tas_Water\ntas_water\nAmount due: $3,006.10\nPlease pay by: 22 Aug 2023\nYour account details\nAccount no.\n240040372\nConnection\n9 Hawkins Street\naddress\nLATROBE TAS\nStatement no. 7716974596\nDate issued\n18/07/2023\nInstallation no. 440012300\nAverage daily usage in kilolitres 3\n2\n1\n0\nJul Oct Jan Apr Jul\nRead period ending\nAmount due: $3,006.10 Please pay by: 22 Aug 2023\nRegister with BPAY View® to view and pay this bill using internet banking Registration No: 3991 2400 4037 22 For assistance contact your financial institution.\n557785-009 000206(8571 :selected:\nTax invoice itemised Billing period 01 Jul 2023 - 30 Sep 2023\nFixed or service charges\nFull Fixed Water Charge - 20mm × 8 (01/07/23-30/09/23)\n$760.48\nFire Service Fixed Charge - 100mm (01/07/23-30/09/23)\n$594.12\nFull Fixed Sewerage Charge x 8 ETs (01/07/23-30/09/23)\n$1,459.36\nSubtotal\n$2,813.96\nVariable usage charges\nVariable Water Charge (17kL @ 1.1376/kL) (19/04/23-30/06/23)\n$19.34\nVariable Water Charge (3kL @ 1.1774/kL) (01/07/23-14/07/23)\n$3.53\nVariable Water Charge (12kL @ 1.1376/kL) (19/04/23-30/06/23)\n$13.65\nVariable Water Charge (2kL @ 1.1774/kL) (01/07/23-14/07/23)\n$2.35\nVariable Water Charge (11kL @ 1.1376/kL) (19/04/23-30/06/23)\n$12.51\nVariable Water Charge (2kL @ 1.1774/kL) (01/07/23-14/07/23)\n$2.35\nVariable Water Charge (21kL @ 1.1376/kL) (19/04/23-30/06/23)\n$23.89\nVariable Water Charge (4kL @ 1.1774/kL) (01/07/23-14/07/23)\n$4.71\nVariable Water Charge (27kL @ 1.1376/kL) (19/04/23-30/06/23)\n$30.72\nVariable Water Charge (5kL @ 1.1774/kL) (01/07/23-14/07/23)\n$5.89\nVariable Water Charge (17kL @ 1.1376/kL) (19/04/23-30/06/23)\n$19.34\nVariable Water Charge (3kL @ 1.1774/kL) (01/07/23-14/07/23)\n$3.53\nVariable Water Charge (14kL @ 1.1376/kL) (19/04/23-30/06/23)\n$15.93\nVariable Water Charge (3kL @ 1.1774/kL) (01/07/23-14/07/23)\n$3.53\nVariable Water Charge (23kL @ 1.1376/kL) (19/04/23-30/06/23)\n$26.16\nVariable Water Charge (4kL @ 1.1774/kL) (01/07/23-14/07/23)\n$4.71\nSubtotal\n$192.14\nTotal\n$3,006.10\nMeter details\nMeter reading Your water usage for this quarter is based on a meter reading\nWays to pay your bill\nAdditional information\nNeed help paying your bill? We can help. Please call us on 13 6992 and we'll help make a plan that works for you.\nEligible for a concession? If you have an eligible concession card, we can apply a discount to your bill. Call us on 13 6992 or apply online at taswater.com.au/concessions\nInterest on overdue amounts Daily interest is charged on overdue amounts from the due date at the monthly 90-day Bank Accepted Bill Rate plus 6%.\nChanged your contact details? Please call us on 13 6992 and we'll update your details or go to taswater.com.au/update\nSelling a property? If you sell your property, you are still liable for TasWater bills until your solicitor or conveyancer lets us know that ownership has changed. For more information, see taswater.com.au/ownership\nReading your meter every 3 months We need to be able to see your meter and access it easily and safely. Please keep your plants pruned around the meter, restrain your pets and leave your gate unlocked. If we can't safely read your meter, we will estimate your water usage for the next bill.\nYour information is private See our website to read our Privacy and Credit Reporting Policy at taswater.com.au/privacy\nHearing or speech impaired? Call us via the National Relay Service: TTY: call 13 3677 then ask for 13 6992. Speak and Listen: call 1300 555 727 then ask for 13 6992.\nNeed an interpreter? TIS National provides immediate phone interpreting services in 160 languages. Call 13 14 50.\nYour account details\nTaswater\nTasmanian Government\ncentrelink\nAccount\nService Tasmania\nPhone 1300 729 859 Billpay code: 8261 Reference: 39912 40040 37231\nCentrepay\nContact Centrelink for setup humanservices.gov.au/ centrepay Reference: 240040372\nBy mail Send this slip with your cheque (no staples) to: GPO Box 1393 Hobart Tas 7001\nRef\nAmount\nPost Billpay\nReceipt\nAustralia Post Pay in store at Australia\n*444 3991 240040372 31\nDate\nPost\nThanks! :selected:

Company: Tasmanian Water and Sewerage Corporation Pty Ltd

stars : 1

Example 2:

context: Taswarer\nTasmanian Water and Sewerage Corporation Pty Ltd ABN 47 162 220 653\nCommunity Housing Limited Att: Accounts Payable 19-23 Prospect Street BOX HILL VIC 3128\nTax invoice summary\nBilling period 01 Jul 2023 - 30 Sep 2023\nFixed charges\n$2,813.96\nVariable usage charges\n$192.14\nGST\n$0.00\nTotal new charges (this bill)\n$3,006.10\nPrevious bill\n$2,896.31\nAdjustments\n-$2,896.31\nTotal\n$3,006.10\nYour current average use is 1.95 kL/day Your current average cost is $2.21/day\nMeter reading Your water usage for this quarter is based on a meter reading\n--- * If you plan to pay in person please do not cut\nTaswarer Payment slip\nAccount no.\n240040372\nConnection address 9 Hawkins Street LATROBE TAS\nDIRECT DEBIT\nDirect Debit\nBPAY BPAY®\nWould you like to receive all TasWater notices digitally? Scan this QR code, or visit: www.taswater.com.au/digital-billing\nPlease phone 13 6992 or visit\nwww.taswater.com.au/payment\nBiller code: 117309\nRef: 3991 2400 4037 22\nAll enquiries & emergencies 13 6992\nemail enquiries@taswater.com.au website www.taswater.com.au post GPO Box 1393 Hobart Tasmania 7001\nf\nTasWater1 Tas_Water\ntas_water\nAmount due: $3,006.10\nPlease pay by: 22 Aug 2023\nYour account details\nAccount no.\n240040372\nConnection\n9 Hawkins Street\naddress\nLATROBE TAS\nStatement no. 7716974596\nDate issued\n18/07/2023\nInstallation no. 440012300\nAverage daily usage in kilolitres 3\n2\n1\n0\nJul Oct Jan Apr Jul\nRead period ending\nAmount due: $3,006.10 Please pay by: 22 Aug 2023\nRegister with BPAY View® to view and pay this bill using internet banking Registration No: 3991 2400 4037 22 For assistance contact your financial institution.\n557785-009 000206(8571 :selected:\nTax invoice itemised Billing period 01 Jul 2023 - 30 Sep 2023\nFixed or service charges\nFull Fixed Water Charge - 20mm × 8 (01/07/23-30/09/23)\n$760.48\nFire Service Fixed Charge - 100mm (01/07/23-30/09/23)\n$594.12\nFull Fixed Sewerage Charge x 8 ETs (01/07/23-30/09/23)\n$1,459.36\nSubtotal\n$2,813.96\nVariable usage charges\nVariable Water Charge (17kL @ 1.1376/kL) (19/04/23-30/06/23)\n$19.34\nVariable Water Charge (3kL @ 1.1774/kL) (01/07/23-14/07/23)\n$3.53\nVariable Water Charge (12kL @ 1.1376/kL) (19/04/23-30/06/23)\n$13.65\nVariable Water Charge (2kL @ 1.1774/kL) (01/07/23-14/07/23)\n$2.35\nVariable Water Charge (11kL @ 1.1376/kL) (19/04/23-30/06/23)\n$12.51\nVariable Water Charge (2kL @ 1.1774/kL) (01/07/23-14/07/23)\n$2.35\nVariable Water Charge (21kL @ 1.1376/kL) (19/04/23-30/06/23)\n$23.89\nVariable Water Charge (4kL @ 1.1774/kL) (01/07/23-14/07/23)\n$4.71\nVariable Water Charge (27kL @ 1.1376/kL) (19/04/23-30/06/23)\n$30.72\nVariable Water Charge (5kL @ 1.1774/kL) (01/07/23-14/07/23)\n$5.89\nVariable Water Charge (17kL @ 1.1376/kL) (19/04/23-30/06/23)\n$19.34\nVariable Water Charge (3kL @ 1.1774/kL) (01/07/23-14/07/23)\n$3.53\nVariable Water Charge (14kL @ 1.1376/kL) (19/04/23-30/06/23)\n$15.93\nVariable Water Charge (3kL @ 1.1774/kL) (01/07/23-14/07/23)\n$3.53\nVariable Water Charge (23kL @ 1.1376/kL) (19/04/23-30/06/23)\n$26.16\nVariable Water Charge (4kL @ 1.1774/kL) (01/07/23-14/07/23)\n$4.71\nSubtotal\n$192.14\nTotal\n$3,006.10\nMeter details\nMeter reading Your water usage for this quarter is based on a meter reading\nWays to pay your bill\nAdditional information\nNeed help paying your bill? We can help. Please call us on 13 6992 and we'll help make a plan that works for you.\nEligible for a concession? If you have an eligible concession card, we can apply a discount to your bill. Call us on 13 6992 or apply online at taswater.com.au/concessions\nInterest on overdue amounts Daily interest is charged on overdue amounts from the due date at the monthly 90-day Bank Accepted Bill Rate plus 6%.\nChanged your contact details? Please call us on 13 6992 and we'll update your details or go to taswater.com.au/update\nSelling a property? If you sell your property, you are still liable for TasWater bills until your solicitor or conveyancer lets us know that ownership has changed. For more information, see taswater.com.au/ownership\nReading your meter every 3 months We need to be able to see your meter and access it easily and safely. Please keep your plants pruned around the meter, restrain your pets and leave your gate unlocked. If we can't safely read your meter, we will estimate your water usage for the next bill.\nYour information is private See our website to read our Privacy and Credit Reporting Policy at taswater.com.au/privacy\nHearing or speech impaired? Call us via the National Relay Service: TTY: call 13 3677 then ask for 13 6992. Speak and Listen: call 1300 555 727 then ask for 13 6992.\nNeed an interpreter? TIS National provides immediate phone interpreting services in 160 languages. Call 13 14 50.\nYour account details\nTaswater\nTasmanian Government\ncentrelink\nAccount\nService Tasmania\nPhone 1300 729 859 Billpay code: 8261 Reference: 39912 40040 37231\nCentrepay\nContact Centrelink for setup humanservices.gov.au/ centrepay Reference: 240040372\nBy mail Send this slip with your cheque (no staples) to: GPO Box 1393 Hobart Tas 7001\nRef\nAmount\nPost Billpay\nReceipt\nAustralia Post Pay in store at Australia\n*444 3991 240040372 31\nDate\nPost\nThanks! :selected:
ABN : 47 152 220 656

stars : 0

Example 3:

context: Taswarer\nTasmanian Water and Sewerage Corporation Pty Ltd ABN 47 162 220 653\nCommunity Housing Limited Att: Accounts Payable 19-23 Prospect Street BOX HILL VIC 3128\nTax invoice summary\nBilling period 01 Jul 2023 - 30 Sep 2023\nFixed charges\n$2,813.96\nVariable usage charges\n$192.14\nGST\n$0.00\nTotal new charges (this bill)\n$3,006.10\nPrevious bill\n$2,896.31\nAdjustments\n-$2,896.31\nTotal\n$3,006.10\nYour current average use is 1.95 kL/day Your current average cost is $2.21/day\nMeter reading Your water usage for this quarter is based on a meter reading\n--- * If you plan to pay in person please do not cut\nTaswarer Payment slip\nAccount no.\n240040372\nConnection address 9 Hawkins Street LATROBE TAS\nDIRECT DEBIT\nDirect Debit\nBPAY BPAY®\nWould you like to receive all TasWater notices digitally? Scan this QR code, or visit: www.taswater.com.au/digital-billing\nPlease phone 13 6992 or visit\nwww.taswater.com.au/payment\nBiller code: 117309\nRef: 3991 2400 4037 22\nAll enquiries & emergencies 13 6992\nemail enquiries@taswater.com.au website www.taswater.com.au post GPO Box 1393 Hobart Tasmania 7001\nf\nTasWater1 Tas_Water\ntas_water\nAmount due: $3,006.10\nPlease pay by: 22 Aug 2023\nYour account details\nAccount no.\n240040372\nConnection\n9 Hawkins Street\naddress\nLATROBE TAS\nStatement no. 7716974596\nDate issued\n18/07/2023\nInstallation no. 440012300\nAverage daily usage in kilolitres 3\n2\n1\n0\nJul Oct Jan Apr Jul\nRead period ending\nAmount due: $3,006.10 Please pay by: 22 Aug 2023\nRegister with BPAY View® to view and pay this bill using internet banking Registration No: 3991 2400 4037 22 For assistance contact your financial institution.\n557785-009 000206(8571 :selected:\nTax invoice itemised Billing period 01 Jul 2023 - 30 Sep 2023\nFixed or service charges\nFull Fixed Water Charge - 20mm × 8 (01/07/23-30/09/23)\n$760.48\nFire Service Fixed Charge - 100mm (01/07/23-30/09/23)\n$594.12\nFull Fixed Sewerage Charge x 8 ETs (01/07/23-30/09/23)\n$1,459.36\nSubtotal\n$2,813.96\nVariable usage charges\nVariable Water Charge (17kL @ 1.1376/kL) (19/04/23-30/06/23)\n$19.34\nVariable Water Charge (3kL @ 1.1774/kL) (01/07/23-14/07/23)\n$3.53\nVariable Water Charge (12kL @ 1.1376/kL) (19/04/23-30/06/23)\n$13.65\nVariable Water Charge (2kL @ 1.1774/kL) (01/07/23-14/07/23)\n$2.35\nVariable Water Charge (11kL @ 1.1376/kL) (19/04/23-30/06/23)\n$12.51\nVariable Water Charge (2kL @ 1.1774/kL) (01/07/23-14/07/23)\n$2.35\nVariable Water Charge (21kL @ 1.1376/kL) (19/04/23-30/06/23)\n$23.89\nVariable Water Charge (4kL @ 1.1774/kL) (01/07/23-14/07/23)\n$4.71\nVariable Water Charge (27kL @ 1.1376/kL) (19/04/23-30/06/23)\n$30.72\nVariable Water Charge (5kL @ 1.1774/kL) (01/07/23-14/07/23)\n$5.89\nVariable Water Charge (17kL @ 1.1376/kL) (19/04/23-30/06/23)\n$19.34\nVariable Water Charge (3kL @ 1.1774/kL) (01/07/23-14/07/23)\n$3.53\nVariable Water Charge (14kL @ 1.1376/kL) (19/04/23-30/06/23)\n$15.93\nVariable Water Charge (3kL @ 1.1774/kL) (01/07/23-14/07/23)\n$3.53\nVariable Water Charge (23kL @ 1.1376/kL) (19/04/23-30/06/23)\n$26.16\nVariable Water Charge (4kL @ 1.1774/kL) (01/07/23-14/07/23)\n$4.71\nSubtotal\n$192.14\nTotal\n$3,006.10\nMeter details\nMeter reading Your water usage for this quarter is based on a meter reading\nWays to pay your bill\nAdditional information\nNeed help paying your bill? We can help. Please call us on 13 6992 and we'll help make a plan that works for you.\nEligible for a concession? If you have an eligible concession card, we can apply a discount to your bill. Call us on 13 6992 or apply online at taswater.com.au/concessions\nInterest on overdue amounts Daily interest is charged on overdue amounts from the due date at the monthly 90-day Bank Accepted Bill Rate plus 6%.\nChanged your contact details? Please call us on 13 6992 and we'll update your details or go to taswater.com.au/update\nSelling a property? If you sell your property, you are still liable for TasWater bills until your solicitor or conveyancer lets us know that ownership has changed. For more information, see taswater.com.au/ownership\nReading your meter every 3 months We need to be able to see your meter and access it easily and safely. Please keep your plants pruned around the meter, restrain your pets and leave your gate unlocked. If we can't safely read your meter, we will estimate your water usage for the next bill.\nYour information is private See our website to read our Privacy and Credit Reporting Policy at taswater.com.au/privacy\nHearing or speech impaired? Call us via the National Relay Service: TTY: call 13 3677 then ask for 13 6992. Speak and Listen: call 1300 555 727 then ask for 13 6992.\nNeed an interpreter? TIS National provides immediate phone interpreting services in 160 languages. Call 13 14 50.\nYour account details\nTaswater\nTasmanian Government\ncentrelink\nAccount\nService Tasmania\nPhone 1300 729 859 Billpay code: 8261 Reference: 39912 40040 37231\nCentrepay\nContact Centrelink for setup humanservices.gov.au/ centrepay Reference: 240040372\nBy mail Send this slip with your cheque (no staples) to: GPO Box 1393 Hobart Tas 7001\nRef\nAmount\nPost Billpay\nReceipt\nAustralia Post Pay in store at Australia\n*444 3991 240040372 31\nDate\nPost\nThanks! :selected:
Billing Address : 1788 dandenong road clayton-3168

stars : 0

Example 4:

context: Taswarer\nTasmanian Water and Sewerage Corporation Pty Ltd ABN 47 162 220 653\nCommunity Housing Limited Att: Accounts Payable 19-23 Prospect Street BOX HILL VIC 3128\nTax invoice summary\nBilling period 01 Jul 2023 - 30 Sep 2023\nFixed charges\n$2,813.96\nVariable usage charges\n$192.14\nGST\n$0.00\nTotal new charges (this bill)\n$3,006.10\nPrevious bill\n$2,896.31\nAdjustments\n-$2,896.31\nTotal\n$3,006.10\nYour current average use is 1.95 kL/day Your current average cost is $2.21/day\nMeter reading Your water usage for this quarter is based on a meter reading\n--- * If you plan to pay in person please do not cut\nTaswarer Payment slip\nAccount no.\n240040372\nConnection address 9 Hawkins Street LATROBE TAS\nDIRECT DEBIT\nDirect Debit\nBPAY BPAY®\nWould you like to receive all TasWater notices digitally? Scan this QR code, or visit: www.taswater.com.au/digital-billing\nPlease phone 13 6992 or visit\nwww.taswater.com.au/payment\nBiller code: 117309\nRef: 3991 2400 4037 22\nAll enquiries & emergencies 13 6992\nemail enquiries@taswater.com.au website www.taswater.com.au post GPO Box 1393 Hobart Tasmania 7001\nf\nTasWater1 Tas_Water\ntas_water\nAmount due: $3,006.10\nPlease pay by: 22 Aug 2023\nYour account details\nAccount no.\n240040372\nConnection\n9 Hawkins Street\naddress\nLATROBE TAS\nStatement no. 7716974596\nDate issued\n18/07/2023\nInstallation no. 440012300\nAverage daily usage in kilolitres 3\n2\n1\n0\nJul Oct Jan Apr Jul\nRead period ending\nAmount due: $3,006.10 Please pay by: 22 Aug 2023\nRegister with BPAY View® to view and pay this bill using internet banking Registration No: 3991 2400 4037 22 For assistance contact your financial institution.\n557785-009 000206(8571 :selected:\nTax invoice itemised Billing period 01 Jul 2023 - 30 Sep 2023\nFixed or service charges\nFull Fixed Water Charge - 20mm × 8 (01/07/23-30/09/23)\n$760.48\nFire Service Fixed Charge - 100mm (01/07/23-30/09/23)\n$594.12\nFull Fixed Sewerage Charge x 8 ETs (01/07/23-30/09/23)\n$1,459.36\nSubtotal\n$2,813.96\nVariable usage charges\nVariable Water Charge (17kL @ 1.1376/kL) (19/04/23-30/06/23)\n$19.34\nVariable Water Charge (3kL @ 1.1774/kL) (01/07/23-14/07/23)\n$3.53\nVariable Water Charge (12kL @ 1.1376/kL) (19/04/23-30/06/23)\n$13.65\nVariable Water Charge (2kL @ 1.1774/kL) (01/07/23-14/07/23)\n$2.35\nVariable Water Charge (11kL @ 1.1376/kL) (19/04/23-30/06/23)\n$12.51\nVariable Water Charge (2kL @ 1.1774/kL) (01/07/23-14/07/23)\n$2.35\nVariable Water Charge (21kL @ 1.1376/kL) (19/04/23-30/06/23)\n$23.89\nVariable Water Charge (4kL @ 1.1774/kL) (01/07/23-14/07/23)\n$4.71\nVariable Water Charge (27kL @ 1.1376/kL) (19/04/23-30/06/23)\n$30.72\nVariable Water Charge (5kL @ 1.1774/kL) (01/07/23-14/07/23)\n$5.89\nVariable Water Charge (17kL @ 1.1376/kL) (19/04/23-30/06/23)\n$19.34\nVariable Water Charge (3kL @ 1.1774/kL) (01/07/23-14/07/23)\n$3.53\nVariable Water Charge (14kL @ 1.1376/kL) (19/04/23-30/06/23)\n$15.93\nVariable Water Charge (3kL @ 1.1774/kL) (01/07/23-14/07/23)\n$3.53\nVariable Water Charge (23kL @ 1.1376/kL) (19/04/23-30/06/23)\n$26.16\nVariable Water Charge (4kL @ 1.1774/kL) (01/07/23-14/07/23)\n$4.71\nSubtotal\n$192.14\nTotal\n$3,006.10\nMeter details\nMeter reading Your water usage for this quarter is based on a meter reading\nWays to pay your bill\nAdditional information\nNeed help paying your bill? We can help. Please call us on 13 6992 and we'll help make a plan that works for you.\nEligible for a concession? If you have an eligible concession card, we can apply a discount to your bill. Call us on 13 6992 or apply online at taswater.com.au/concessions\nInterest on overdue amounts Daily interest is charged on overdue amounts from the due date at the monthly 90-day Bank Accepted Bill Rate plus 6%.\nChanged your contact details? Please call us on 13 6992 and we'll update your details or go to taswater.com.au/update\nSelling a property? If you sell your property, you are still liable for TasWater bills until your solicitor or conveyancer lets us know that ownership has changed. For more information, see taswater.com.au/ownership\nReading your meter every 3 months We need to be able to see your meter and access it easily and safely. Please keep your plants pruned around the meter, restrain your pets and leave your gate unlocked. If we can't safely read your meter, we will estimate your water usage for the next bill.\nYour information is private See our website to read our Privacy and Credit Reporting Policy at taswater.com.au/privacy\nHearing or speech impaired? Call us via the National Relay Service: TTY: call 13 3677 then ask for 13 6992. Speak and Listen: call 1300 555 727 then ask for 13 6992.\nNeed an interpreter? TIS National provides immediate phone interpreting services in 160 languages. Call 13 14 50.\nYour account details\nTaswater\nTasmanian Government\ncentrelink\nAccount\nService Tasmania\nPhone 1300 729 859 Billpay code: 8261 Reference: 39912 40040 37231\nCentrepay\nContact Centrelink for setup humanservices.gov.au/ centrepay Reference: 240040372\nBy mail Send this slip with your cheque (no staples) to: GPO Box 1393 Hobart Tas 7001\nRef\nAmount\nPost Billpay\nReceipt\nAustralia Post Pay in store at Australia\n*444 3991 240040372 31\nDate\nPost\nThanks! :selected:
Billing Address : Community Housing Limited Att : Accounts Payable 19-23 Prospect Street BOX HILL VIC 3128

stars : 1
context: {context}

Use the context to score the stars for attribute and answer and just give star values
{attribute}:{answer}
stars:
'''


def generate_invoice_response(template, invoice_example, processed_json, input_invoice):
    """
    Generates a chat response using the specified template and input data.

    Parameters:
    template (str): Template for formatting the chat prompt.
    invoice_example (str): Input invoice example data.
    processed_json (str): Processed JSON data.
    input_invoice (str): Input invoice information.

    Returns:
    str: Chat response generated by GPT-4 model.
    """
    gpt4_prompt = PromptTemplate(
        template=template,
        input_variables=["input", "output", "input_invoice"]
    )

    system_message_prompt = SystemMessagePromptTemplate(prompt=gpt4_prompt)

    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt])

    # Format the chat prompt using the provided input data
    messages = chat_prompt.format_prompt(input=invoice_example, output=processed_json, input_invoice=input_invoice).to_messages()

    # Create a GPT-4 chat instance
    chat = ChatOpenAI(engine="gpt-4-32k", temperature=0)

    # Generate the chat response using the formatted messages
    resp = chat(messages)

    # Return the content of the response
    return resp.content

def extract_attributes(json_data, parent_key=''):
    """
    Recursively extracts attributes and their corresponding answers from a JSON object.
    
    Args:
        json_data (dict): The JSON object to extract attributes from.

    Returns:
        list: A list of dictionaries, where each dictionary represents an attribute and its answer.
    """
    attributes_list = []
    if isinstance(json_data, dict):
        for key, value in json_data.items():
            new_key = f"{key}" if parent_key else key
            if isinstance(value, list):
                for item in value:
                    attributes_list.extend(extract_attributes(item, new_key))
            elif isinstance(value, dict):
                attributes_list.extend(extract_attributes(value, new_key))
            else:
                attributes_list.append({new_key: value})
    return attributes_list

def download_blob_from_storage(blob_path):
    
    blob_service_client = BlobServiceClient.from_connection_string(os.environ['AZURE_STORAGE_CONNECTION_STRING'])

# Get a client to interact with the specified container
    container_client = blob_service_client.get_container_client(os.environ['BLOB_CONTAINER_NAME'])

    # Get a client to interact with the specified blob
    blob_client = container_client.get_blob_client(blob_path.replace(f"{os.environ['BLOB_CONTAINER_NAME']}/",""))

    # Download the blob's content
    with io.BytesIO() as input_stream:
    # Download the blob to the stream
        downloader = blob_client.download_blob()
        
        # Write the blob's data into the stream
        downloader.readinto(input_stream)
        
        # Seek to the beginning of the stream
        input_stream.seek(0)
        
        # Load the stream data into a pandas DataFrame
        df = pd.read_excel(input_stream)

    json_str = df.apply(lambda x: [x.dropna()], axis=1).to_json(orient='index', date_format='iso')
    return json_str

def evaluation(template_1, format_json_output, raw_invoice_data):
    """
    Evaluates the correctness of extracted information by comparing it with a predefined template 
    and raw invoice data using the GPT-3.5 Turbo engine.

    Parameters:
    template_1 (str): A predefined template used for generating prompts.
    format_json_output (list): A list of dictionaries containing formatted extracted information.
    raw_invoice_data (dict): Raw invoice data used as context for the evaluation.

    Returns:
    tuple: A tuple containing two lists - the first list (scoring) contains evaluation scores,
           and the second list (wrong_answers) contains extracted answers identified as incorrect.
    """

    # Define GPT-3.5 Turbo prompt templates for generating messages
    gpt3_5_prompt = PromptTemplate(
                    template=template_1,
                    input_variables=["context", "attribute", "answer"]
                )
    system_message_prompt = SystemMessagePromptTemplate(prompt=gpt3_5_prompt)
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt])

    # Initialize lists to store evaluation scores and wrong answers
    scoring = []
    wrong_answers = []
    
    # Iterate through the formatted extracted information
    for dict in format_json_output:
        # Generate messages using the predefined prompts and extracted information
        for key, value in dict.items():
            messages = chat_prompt.format_prompt(context=raw_invoice_data, attribute=key, answer=value).to_messages()
            question=key
            print(question)
            chat = ChatOpenAI(engine="gpt-4-32k", temperature=0)
            
            # Generate response using GPT-3.5 Turbo
            resp = chat(messages)

            # Evaluate the response
            if resp.content == '0':
                # If the response indicates incorrect answer, store the answer and title
                wrong_answers.append({key: value})
            # Store the response content (evaluation score) in the scoring list
            scoring.append(resp.content)

    # Return the evaluation scores and wrong answers as a tuple
    return scoring, wrong_answers


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    if req.method == "POST":
        # Handle POST request
        try:
            req_body = req.get_json()
            raw_invoice_example = req_body["raw_invoice_example"]
            invoice_example_excel = req_body["excel_example"]
            raw_invoice_input = req_body["raw_invoice_input"]
            excel_json = download_blob_from_storage(invoice_example_excel)

            llmoutput = generate_invoice_response(template,raw_invoice_example,excel_json,raw_invoice_input)
            llm_json = json.loads(llmoutput)
            print(llm_json)
            attributes_list = extract_attributes(llm_json)
            print(attributes_list)
            evaluation_results = evaluation(template_1,attributes_list,raw_invoice_input)
            print(evaluation_results)
            Incorrect_results = evaluation_results[1]
            relevance_scoring = sum(int(number) for number in evaluation_results[0])/len(evaluation_results[0])

            # If average is less than 1, set it to 0
            if relevance_scoring < 1:
                relevance_scoring = 0
            print(relevance_scoring)
            final_output = {
                "invoice_result" : llm_json,
                "relevance_scoring" : relevance_scoring,
                "incorrect_results" : Incorrect_results
            }


            logging.info(final_output)
            print(final_output)
            return func.HttpResponse(
                json.dumps(final_output),
            #    relevance_scoring,
                mimetype="application/json",
            )

        except ValueError:
            return func.HttpResponse(
                 "Invalid request body",
                 status_code=400
            )
    
    return func.HttpResponse(
                 "Invalid request body",
                 status_code=400
            )

    
