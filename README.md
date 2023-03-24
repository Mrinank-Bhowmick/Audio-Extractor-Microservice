<h1>Audio Extractor Microservice </h1>

The Audio Extractor Microservice is an API that allows you to extract the audio track from a video file and convert it to MP3. This can be useful if you want to listen to the audio from a video file on a device that does not support the video format or if you want to extract just the audio track to use in a different project.

<h2>Usage</h2>

[https://audioextractor.vercel.app/](https://audioextractor.vercel.app/) - This is the base URL for the API. You can use this URL to test the API.

[https://audioextractor.vercel.app/login](https://audioextractor.vercel.app/login) - This is the login URL for the API which will return JWT Token. You can use this URL to login to the server.

[https://audioextractor.vercel.app/upload](https://audioextractor.vercel.app/upload) - This is the upload URL for the API. You can use this URL to upload a video file to the server.


# Api Documentation
<details close="">
<summary>
 <g-emoji class="emoji" alias="Login ">🌐</g-emoji>
  <strong>Login : </strong>
</summary>

```
curl -X POST http://mp3convertor.mrinank-bhowmick.cloud.okteto.net/login -u username:password

- This will return a JWT Token which you can use to access the server.
```

</details>

<Br>

<details close="">
<summary>
 <g-emoji class="emoji" alias="upload">🌐</g-emoji>
  <strong>Upload : </strong>
</summary>

```
curl -X POST -F 'file=@./path/to/file' -H 'Authorization: Bearer <token>' http://mp3convertor.mrinank-bhowmick.cloud.okteto.net/upload
```

</details>

<br>

<details close="">
<summary>
 <g-emoji class="emoji" alias="upload">🌐</g-emoji>
  <strong>Download : </strong>
</summary>
    
    ```
    curl -X GET -H 'Authorization: Bearer <token>' http://mp3convertor.mrinank-bhowmick.cloud.okteto.net/download?fid=<file_id> --output <file_name>.mp3
    ```

<h2>Licence</h2>

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details