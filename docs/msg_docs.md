#retract a message

{
	'from': 'PROFILE_ID@chat.grindr.com/something', 
	'body': {
	'body': '{
		"targetMessageId":"UUID_OF_MESSAGE_TO_BE_RETRACTED"}', 
		'messageContext': '', 
		'messageId': 'UUID', 
		'replyMessageBody': '', 
		'replyMessageId': '', 
		'replyMessageName': '', 
		'replyMessageType': '', 
		'sourceProfileId': 'PROFILE_ID', 
		'targetProfileId': 'PROFILE_ID', 
		'timestamp': UNIX_TIMESTAMP, 
		'type': 'retract', 
	}
}

#expiring image

{
	'from': 'PROFILE_ID@chat.grindr.com/something', 
	'body': {
		'body': '{"duration":10000,"imageHash":"SOME_HASH"}', 
		'messageContext': '', 
		'messageId': 'UUID', 
		'replyMessageBody': '', 
		'replyMessageId': '', 
		'replyMessageName': '', 
		'replyMessageType': '', 
		'sourceProfileId': 'PROFILE_ID', 
		'targetProfileId': 'PROFILE_ID', 
		'timestamp': UNIX_TIMESTAMP, 
		'type': 'expiring_image', 
	}
}


