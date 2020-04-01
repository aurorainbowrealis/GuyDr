# URL Documentation

URL: /v4/views/{profileId}
Method: POST
Purpose: Informs the server that you have viewed that profile

URL: /v3/me/chat/messages?undelivered=true&receipts=true&limit=250&from=0
Method: GET
Data: {
	"undelivered": true,
	"receipts": true,
	"limit": 250
}
Purpose: Collect messages received while offline

URL: /v3/me/chat/messages?confirmed=true 
Method: PUT
Data: {"confirmed": true}
Purpose: Confirm we have collected old messages

# Standards for creating functions in each language

## Javascript

Functions:
	Write using camel case, e.g fooBar()

Classes:
	Write using camel case with the first letter uppercase, e.g. FooBar()

Variables:
	Write all lower case, e.g. foo

## Python

Functions:
	Write using underscores, e.g. foo_bar()

Classes:
	Write using camel case with the first letter uppercase

Variables:
	Write all lower case, e.g. foo