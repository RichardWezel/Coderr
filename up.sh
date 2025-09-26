git add .
git commit -m "$*"
git push
ssh coderr-server "cd projects/Coderr && git pull"