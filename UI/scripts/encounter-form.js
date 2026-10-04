document.addEventListener('DOMContentLoaded',()=>{
    
    const profile=JSON.parse(localStorage.getItem('facebingo_profile')||'null');
    if(!profile?.name){
        location.assign('/');
        return;
    }

    document.querySelector('#your-name').value=profile.name; 
    
    const panels={camera:document.querySelector('#panel-camera'),upload:document.querySelector('#panel-upload')},video=document.querySelector('#webcam-video');
    let stream;
    
    document.querySelectorAll('[data-photo-tab]').forEach(b=>b.addEventListener('click',()=>{
        const cam=b.dataset.photoTab==='camera';
        panels.camera.classList.toggle('active',cam);
        panels.upload.classList.toggle('active',!cam);
        if(!cam)stream?.getTracks().forEach(t=>t.stop());
    }));
    
    startCamera.addEventListener('click',async()=>{
        try{
            stream=await navigator.mediaDevices.getUserMedia({video:{facingMode:'user'},audio:false});
            video.srcObject=stream;snapPhoto.hidden=false;
        }catch{
            formError.hidden=false;
            formError.textContent='Camera unavailable. Please upload a photo.';
        }
    });

    snapPhoto.addEventListener('click',()=>{
        const c=snapCanvas;
        c.width=video.videoWidth;
        c.height=video.videoHeight;
        c.getContext('2d').drawImage(video,0,0);
        c.toBlob(blob=>{
            const d=new DataTransfer();
            d.items.add(new File([blob],'selfie.jpg',{type:'image/jpeg'}));
            photoFile.files=d.files;
        },
        'image/jpeg',
        0.85
    );
});
});
