#
wrangler r2 bucket notification create deepmodeling-docs \
  --event-type object-create \
  --queue deepmodeling-docs-event-queue

wrangler r2 object put deepmodeling-docs/test.txt --file test.txt --remote 

npx wrangler deploy