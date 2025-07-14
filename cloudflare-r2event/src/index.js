// export default {
//     async queue(batch, env) {
//       console.log(`Processing ${batch.messages.length} file events`);
      
//       for (const message of batch.messages) {
//         try {
//           const event = message.body;

//           const s3_object_key = event.object.key;
//           const s3_bucket_endpoint = env.R2_PUBLIC_URL;

//           const s3_pdf_url = `${s3_bucket_endpoint}/${s3_object_key}`;

//         //   const response = await fetch(env.WEBHOOK_URL, {
          
//           // 转发到你的主服务
//           const response = await fetch(env.WEBHOOK_URL, {
//             method: 'POST',
//             headers: {
//               'Content-Type': 'application/json',
//               'User-Agent': 'DeepModeling-Docs-Worker'
//             },
//             // const object_url = event.object
//             body: JSON.stringify({
//                 bucket: event.bucket,
//                 object: event.object.key,
//                 action: event.action,
//                 eventTime: event.eventTime,
//                 objectSize: event.object.size, 
//                 etag: event.object.eTag, // usually md5sum of the file for small files
//                 md5sum: event.checksums.md5,
//                 account: event.account
//               })
//           });
          
//           if (response.ok) {
//             console.log(`Successfully forwarded: ${event.object.key}`);
//             message.ack();
//           } else {
//             console.error(`Webhook failed: ${response.status}`);
//             message.retry();
//           }
//         } catch (error) {
//           console.error('Error processing message:', error);
//           message.retry();
//         }
//       }
//     }
//   }


// export default {
//   async fetch(request, env) {
//       const event = await request.json();
      
//       // 只处理 PDF 上传事件
//       if (event.action === 'PutObject' && event.object.key.endsWith('.pdf')) {
          
//           // 触发 Prefect 工作流
//           const response = await fetch(`${env.PREFECT_API_URL}/deployments/${env.DEPLOYMENT_ID}/create_flow_run`, {
//               method: 'POST',
//               headers: {
//                   'Content-Type': 'application/json',
//                   'Authorization': `Bearer ${env.PREFECT_API_KEY}`
//               },
//               body: JSON.stringify({
//                   parameters: {
//                       s3_pdf_url: `https://deepmodeling-docs-r2.deepmd.us/${event.object.key}`
//                   }
//               })
//           });
          
//           const result = await response.json();
//           console.log('Flow run created:', result.id);
          
//           return new Response('OK');
//       }
      
//       return new Response('Ignored');
//   }
// };

async function getDeploymentByName(flowName, deploymentName, env) {
  const url = `${env.PREFECT_API_URL}/deployments/name/${flowName}/${deploymentName}`;
  console.log('Getting deployment:', url);
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Basic ${btoa(env.PREFECT_API_AUTH_STRING)}`
    }
  });
  
  if (response.ok) {
    const deployment = await response.json();
    console.log(`Found deployment ID: ${deployment.id}`);
    return deployment.id;
  } else {
    const errorText = await response.text();
    throw new Error(`Failed to get deployment: ${response.status} - ${errorText}`);
  }
}

export default {
  async queue(batch, env) {
    console.log(`Processing ${batch.messages.length} file events`);
    // Get deployment ID by name
    const deploymentId = await getDeploymentByName(
      env.PREFECT_FLOW_NAME || 'workflow-handle-pdf-to-db-and-fastgpt',
      env.PREFECT_DEPLOYMENT_NAME || 'zeabur-deploy-workflow-handle-pdf-to-db-and-fastgpt',
      env
    );

    console.log('deploymentId:', deploymentId);
    
    for (const message of batch.messages) {
      try {
        const event = message.body;
        
        // Only process PDF files
        // if (!event.object.key.endsWith('.pdf')) {
        //   console.log(`Skipping non-PDF file: ${event.object.key}`);
        //   message.ack();
        //   continue;
        // }
        
        const s3_object_url = `${env.R2_PUBLIC_URL}/${event.object.key}`;
        
        // Create flow run with deployment ID
        const apiUrl = `${env.PREFECT_API_URL}/deployments/${deploymentId}/create_flow_run`;
        console.log('Calling Prefect API:', apiUrl);
        console.log('For file:', event.object.key);

        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Basic ${btoa(env.PREFECT_API_AUTH_STRING)}`
            },
            body: JSON.stringify({
                parameters: {
                    s3_object_url: s3_object_url
                }
            })
        });
        
        console.log('Response status:', response.status);
        console.log('Response headers:', Object.fromEntries(response.headers));
        
        if (response.ok) {
          const result = await response.json();
          console.log(`Flow run created: ${result.id}`);
          message.ack();
        } else {
          const errorText = await response.text();
          console.error(`API failed: ${response.status} - ${errorText}`);
          message.retry();
        }
      } catch (error) {
        console.error('Error processing message:', error);
        message.retry();
      }
    }
  }
}