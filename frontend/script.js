var apiEndpoint = "https://mum-mum-idilis.herokuapp.com/"
var urlParams;
var dataFromApi;
var itemPriceFromApi;
var current_page = 0;
var item_counter = {};
var item_name = {};
var item_price = {};
var page_states = {}
var max_pg_seen = 0;

window.addEventListener("resize", resizeFunc);

function resizeFunc(){
    
}

function loadFunc() {
    var match,
        pl     = /\+/g,  // Regex for replacing addition symbol with a space
        search = /([^&=]+)=?([^&]*)/g,
        decode = function (s) { return decodeURIComponent(s.replace(pl, " ")); },
        query  = window.location.search.substring(1);
  
    urlParams = {};
    var apiResult = false;
    while (match = search.exec(query))
       urlParams[decode(match[1])] = decode(match[2]);
    const response = $.ajax({url: apiEndpoint+'populate_menu/'+urlParams['identifier'],success: function(response){
            console.log(response)
            if (response['success']){
                var mainTitle = document.getElementById("sp-name");
                mainTitle.textContent = response['data']['store_name']

                var goLeft = document.getElementById("go-left");
                goLeft.style.visibility = "none";

                var goRight = document.getElementById("go-right");
                goRight.style.visibility = "none";

                var placeOrder = document.getElementById("place-order");
                placeOrder.style.visibility = "none";

                dataFromApi = response['data']['menu_items']; // Currently mocked, replace with api call.
                itemPriceFromApi = response['data']['item_price'];

                for(var i=1;i<=Math.min(4, dataFromApi.length);i+=1){
                var rowElement = document.createElement("div");
                rowElement.className = "row row_menu";
                rowElement.id = "row_"+i;

                var element1 = document.createElement("div");
                element1.className="col-lg-8 items";
                element1.id="item-"+i;

                var element1pt1 = document.createElement("span");
                element1pt1.className='price-br';
                element1pt1.id='item_price-'+i;

                element1.appendChild(element1pt1);
                rowElement.appendChild(element1);


                var element2 = document.createElement("div");
                element2.className="col-lg-4 items";
                var input1 = document.createElement("input");
                var span = document.createElement("span");
                var input2 = document.createElement("input");

                input1.type = "image";
                input1.className="icon";
                input1.src="../frontend/misc/minus-solid.svg";
                input1.id="dec_"+i;
                input2.type = "image";
                input2.className="icon";
                input2.src="../frontend/misc/plus-solid.svg"
                input2.id="inc_"+i;

                span.id="qty_"+i;
                span.style="padding-left: 0.5vmin; padding-right: 0.5vmin"

                element2.appendChild(input1);
                element2.appendChild(span);
                element2.appendChild(input2);

                rowElement.appendChild(element2);

                document.getElementById("menu").appendChild(rowElement);


                $('#item-'+i).text(dataFromApi[i-1]);
                $('#item_price-'+i).text(itemPriceFromApi[i-1]);
                $('#qty_'+i).text(0);
                item_name[current_page+"_"+i] =  $('#item-'+i).text();
                item_price[current_page+"_"+i] = $('#item_price-'+i).text();
                item_counter[current_page+"_"+i] = 0;
            }
        }
        else{
            console.log(response)
            var mainTitle = document.getElementById("sp-name");
            mainTitle.textContent = "Somethin's wrong!"

            var goLeft = document.getElementById("go-left");
            goLeft.style.visibility = "hidden";

            var goRight = document.getElementById("go-right");
            goRight.style.visibility = "hidden";

            var placeOrder = document.getElementById("place-order");
            placeOrder.style.visibility = "hidden";
        }
    }, error : function(){
            console.log(response)
            var mainTitle = document.getElementById("sp-name");
            mainTitle.textContent = "Somethin's wrong!"

            var goLeft = document.getElementById("go-left");
            goLeft.style.visibility = "hidden";

            var goRight = document.getElementById("go-right");
            goRight.style.visibility = "hidden";

            var placeOrder = document.getElementById("place-order");
            placeOrder.style.visibility = "hidden";
        }
    });
}

$(document).on('click', 'input', 'button',function(e){
    var idClicked = e.target.id;
    if(idClicked==='place-order'){
        const response = $.ajax({url: apiEndpoint+'place_order/'+urlParams['identifier'],
        method: 'POST',
        data: JSON.stringify(item_counter),
        contentType: 'application/json; charset=utf-8',
        dataType: 'json',
        success: function(response){
            console.log(response)
            var goLeft = document.getElementById("go-left");
            goLeft.style.visibility = "hidden";

            var goRight = document.getElementById("go-right");
            goRight.style.visibility = "hidden";

            var placeOrder = document.getElementById("place-order");
            placeOrder.style.visibility = "hidden";

            var childCount = document.getElementById("menu").childElementCount
            for(var i=1;i<childCount+1;i+=1){
                document.getElementById("row_"+i).remove();
            }
            if(response['success']){
                var mainTitle = document.getElementById("sp-name");
                mainTitle.textContent = "Your order is placed!"
            }
            else{
                var mainTitle = document.getElementById("sp-name");
                mainTitle.textContent = "Somethin's wrong!"
            }
        },
        error: function(){
            console.log(response)
            var mainTitle = document.getElementById("sp-name");
            mainTitle.textContent = "Somethin's wrong!"

            var goLeft = document.getElementById("go-left");
            goLeft.style.visibility = "hidden";

            var goRight = document.getElementById("go-right");
            goRight.style.visibility = "hidden";

            var placeOrder = document.getElementById("place-order");
            placeOrder.style.visibility = "hidden";

            var childCount = document.getElementById("menu").childElementCount
            for(var i=1;i<childCount+1;i+=1){
                document.getElementById("row_"+i).remove();
            }
        }
    })
    }
    if(idClicked==='go-left' && current_page>0){
        current_page -=1;
        childElementCount = document.getElementById("menu").childElementCount;
        requiredElement = Math.min(4, dataFromApi.slice(current_page*4).length);
        console.log(requiredElement, childElementCount)
        if (requiredElement>childElementCount){
            for(var i=childElementCount+1; i<=4; i+=1){
                var rowElement = document.createElement("div");
                rowElement.className = "row row_menu";
                rowElement.id = "row_"+i;

                var element1 = document.createElement("div");
                var element1pt1 = document.createElement("div");
                element1pt1.className='price-br';
                element1pt1.id='item_price-'+i;
                element1.appendChild(element1pt1);
                element1.className="col-lg-8 items";
                element1.id="item-"+i;
                rowElement.appendChild(element1);


                var element2 = document.createElement("div");
                element2.className="col-lg-4 items";
                var input1 = document.createElement("input");
                var span = document.createElement("span");
                var input2 = document.createElement("input");

                input1.type = "image";
                input1.className="icon";
                input1.src="../frontend/misc/minus-solid.svg";
                input1.id="dec_"+i;
                input2.type = "image";
                input2.className="icon";
                input2.src="../frontend/misc/plus-solid.svg"
                input2.id="inc_"+i;

                span.id="qty_"+i;
                span.style="padding-left: 0.5vmin; padding-right: 0.5vmin"

                element2.appendChild(input1);
                element2.appendChild(span);
                element2.appendChild(input2);

                rowElement.appendChild(element2);

                document.getElementById("menu").appendChild(rowElement);
            }
        
        }
        for(var i=1;i<=4;i+=1){
            $('#item-'+i).text(item_name[current_page+"_"+i]);
            $('#item_price-'+i).text(item_price[current_page+"_"+i]);
            $('#qty_'+i).text(item_counter[current_page+"_"+i]);
        }
    }
    if(idClicked==='go-right' && current_page+1<Math.round(dataFromApi.length)/4){
        current_page+=1;
        childElementCount = document.getElementById("menu").childElementCount;
        requiredElement = Math.min(4, dataFromApi.slice(current_page*4).length);
        console.log(requiredElement, childElementCount)

        if (requiredElement>childElementCount){
            for(var i=childElementCount+1; i<=4; i+=1){
                var rowElement = document.createElement("div");         
                rowElement.className = "row row_menu";
                rowElement.id = "row_"+i;

                var element1 = document.createElement("div");
                var element1pt1 = document.createElement("div");
                element1pt1.className='price-br';
                element1pt1.id='item_price-'+i;
                element1.appendChild(element1pt1);
                element1.className="col-lg-8 items";
                element1.id="item-"+i;
                rowElement.appendChild(element1);


                var element2 = document.createElement("div");
                element2.className="col-lg-4 items";
                var input1 = document.createElement("input");
                var span = document.createElement("span");
                var input2 = document.createElement("input");

                input1.type = "image";
                input1.className="icon";
                input1.src="../frontend/misc/minus-solid.svg";
                input1.id="dec_"+i;
                input2.type = "image";
                input2.className="icon";
                input2.src="../frontend/misc/plus-solid.svg"
                input2.id="inc_"+i;

                span.id="qty_"+i;
                span.style="padding-left: 0.5vmin; padding-right: 0.5vmin"

                element2.appendChild(input1);
                element2.appendChild(span);
                element2.appendChild(input2);

                rowElement.appendChild(element2);

                document.getElementById("menu").appendChild(rowElement);
                }
        }
        if(childElementCount>requiredElement){
            for(var i=4; i>requiredElement; i-=1){
                document.getElementById("row_"+i).remove();
            }
        }
        for(var i=1;i<=requiredElement;i+=1){
            if(max_pg_seen>=current_page){
                $('#item-'+i).text(item_name[current_page+"_"+i]);
                $('#item_price-'+i).text(itemPriceFromApi[current_page+"_"+i]);
                $('#qty_'+i).text(item_counter[current_page+"_"+i]);
            }
            else{
                $('#item-'+i).text(dataFromApi[current_page*4+i-1]);
                $('#item_price-'+i).text(itemPriceFromApi[current_page*4+i-1]);
                $('#qty_'+i).text(0);
                item_name[current_page+"_"+i] =  $('#item-'+i).text();
                item_price[current_page+"_"+i] = $('#item_price-'+i).text();
                item_counter[current_page+"_"+i] = $('#qty_'+i).text();
            }
        }
        max_pg_seen = Math.max(current_page, max_pg_seen);
    }

    if(idClicked.split('_')[0]==='inc'){
        console.log("Hii")
        item_counter[current_page+"_"+idClicked.split('_')[1]] = parseInt(item_counter[current_page+"_"+idClicked.split('_')[1]])+1;
        $('#qty_'+idClicked.split('_')[1]).text(item_counter[current_page+"_"+idClicked.split('_')[1]]);
        console.log(item_counter[current_page+"_"+idClicked.split('_')[1]])

    }
    if(idClicked.split('_')[0]==='dec'){
        item_counter[current_page+"_"+idClicked.split('_')[1]] = parseInt(item_counter[current_page+"_"+idClicked.split('_')[1]])-1;
        item_counter[current_page+"_"+idClicked.split('_')[1]] = Math.max(item_counter[current_page+"_"+idClicked.split('_')[1]],0);
        $('#qty_'+idClicked.split('_')[1]).text(item_counter[current_page+"_"+idClicked.split('_')[1]]);
    }
        
});

