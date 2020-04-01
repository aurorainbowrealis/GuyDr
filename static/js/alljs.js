var map
var heatmap;
var r_size = 12000;
var heatmap = [];
var pinpoints = [];
let global_socket = null;
var recipient = null;

/**
*  Calls the backend and adds the result to an element in the frontend
* @param {string} address : a backend route e.g. /foo
* @param {string} divId :  a element id e.g. #bar
* @param {string} mode : [set,append] chooses the mode of adding info to the frontend
* @param {dict} args : any args to be used by the backend
* @param {bool} debug : shows debug messages
* @param {function} callback : a callback function called in case of success
*/
function addResult(address, element, mode = 'set', args = {}, debug_=false, callback=undefined) {
    if (debug_) console.log(address)
    $.ajax({
        data: args,
        type: 'GET' || args.type,
        url: address
    })
    .done(function (data) {
        if (debug_) console.log(data)
        if (mode == 'append') $(element).append(data)
        else if (mode == 'set') $(element).html(data)
        if (debug_) console.log(address + ' ended')
        if (callback != undefined) callback()
    })
    .fail(function (jqXHR, textStatus, errorThrown) {
        let errorMessage = textStatus.charAt(0).toUpperCase() + textStatus.slice(1) + ": " + errorThrown
        console.log(errorMessage)
    });
}


/**
*
*/
function chooseScreen(element){
    console.log(element)
    $(".on-mobile").removeClass('d-block d-flex w-100')
    $(".on-mobile").addClass('d-none')
    $(element).removeClass('d-none')
    $(element).addClass('d-flex w-100 p-0')
}


/**
*
*/
function loadProfile(pid) {
    addResult('/get_single_profile', '#single-profile', 'set', { uid: pid }, false, function(){
        $('.carousel').carousel({
          interval: 5000
        })
        chooseScreen('#single-profile-container')
    })
}


/**
*
*/
function getProfileGrid() {
    console.log('profile-grid')
    addResult('/get_profile_grid', '#profile-grid', 'set', {},false, function(){
        $('a.thumbnail').click(function(e)
        {
            e.preventDefault();
        });
    })
}


function getChatHeads(){
    addResult('/get_chat_heads', '.inbox_people','set', {},false, function(){
        $('a.thumbnail').click(function(e){
            e.preventDefault();
        });

    })
}


/*
* My improved version of an answer found in:
* https://stackoverflow.com/questions/270612/scroll-to-bottom-of-div
*/
function scrollSmoothToBottom (element) {
    try{
        $(element).animate({
           scrollTop: $(element)[0].scrollHeight - $(element)[0].clientHeight
        }, 500);
    }catch(err){
        console.log("No active window")
    }
}


function getChats(pid) {
    addResult('/user_chats', '.mesgs', 'set', { 'uid': pid }, false, function(){
        chooseScreen('#chat-screen')  
        recipient = pid + "@chat.grindr.com"
        scrollSmoothToBottom('.msg_history')


        $('#send_msg').on("keyup", function(e) {
            if (e.keyCode == 13) {
                sendChat()
            }
        });
    })
}


function renderMessage(msg){
    addResult('/render_message', '.msg_history', 'append', msg, false, function(){
        scrollSmoothToBottom('.msg_history')
    })
}


function sendChat() {
    
    let user_input = $('input.write_msg').val()
    if (user_input == '')
        return

    var msg = { "body": user_input, "targetProfileId": recipient, "type":"text" }
    console.log(msg)
    renderMessage(msg)
    global_socket.emit('message', msg)
    
    $('input.write_msg').val('').focus()
}


function socketConnect(){
    console.log('Trying to connect')
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    var last_msg = {'body':{'messageId':''}}
    
    socket.on('connect', function () {
        console.log('User Connected')
        socket.emit('message', { body: 'User Connected' })
        global_socket = socket;
    })
    //when receives message
    socket.on('message', function (msg) {
        $('#myAudio')[0].play();

        if (msg.messageId == last_msg.messageId)
            return

        if (msg.sourceProfileId+'@chat.grindr.com' == recipient){
            renderMessage(msg)
            scrollSmoothToBottom('.msg_history')
        }
        last_msg = msg
        getChatHeads()
    })

}



$(function(){
    getChatHeads()
    getProfileGrid()
    socketConnect()
})

