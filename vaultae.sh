data=$(vault write $VAULT_KEY01 ttl=120m -format=json)
export AWS_ACCESS_KEY_ID=$(echo $data | jq -r '.data.access_key')
export AWS_SECRET_ACCESS_KEY=$(echo $data | jq -r '.data.secret_key')
export AWS_SESSION_TOKEN=$(echo $data | jq -r '.data.security_token')
