// get data by pagination
$(".paginate_by").click(function(e){
    let paginate = e.target.getInnerHTML();
    console.log(paginate)
    //debugger;
    let path = window.location.pathname;
    let urlParams = new URLSearchParams(window.location.search);

    if(urlParams.has('paginate_by')){
        urlParams.set('paginate_by', paginate);
    }else{
        urlParams.append('paginate_by', paginate);
    }
    let newUrl = path + '?' + urlParams.toString();
    window.location.href = newUrl;
});