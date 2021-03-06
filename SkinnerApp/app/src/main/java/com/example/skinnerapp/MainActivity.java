package com.example.skinnerapp;

import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import androidx.core.content.FileProvider;

import android.Manifest;
import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.util.Base64;
import android.util.JsonReader;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import com.example.skinnerapp.Interface.JsonPlaceHolderApi;
import com.example.skinnerapp.Model.AnalizarImagenRequest;
import com.example.skinnerapp.Model.AnalizarImagenResponse;

import java.io.BufferedInputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;

public class MainActivity extends AppCompatActivity {
    private ImageView takePictureButton;
    private ImageView imageView;
    static final int REQUEST_TAKE_PHOTO = 1;
    private String currentPhotoPath;
    private ImageView btnAnalizar;
    private TextView textView;
    private File f;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        takePictureButton = (ImageView) findViewById(R.id.button_image);
        imageView = (ImageView) findViewById(R.id.imageview);
        textView = (TextView) findViewById(R.id.text_call);


        btnAnalizar = (ImageView) findViewById(R.id.button_analizar);
        btnAnalizar.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                callService();
            }
        });
        btnAnalizar.setVisibility(View.GONE);
        takePictureButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                askCameraPermissions();
            }
        });
    }

    private void callService() {
                Retrofit retrofit = new Retrofit.Builder()
                .baseUrl("https://skinnerserver.herokuapp.com/")
                .addConverterFactory(GsonConverterFactory.create())
                .build();

        JsonPlaceHolderApi service = retrofit.create(JsonPlaceHolderApi.class);

        AnalizarImagenRequest req = new AnalizarImagenRequest(convertImgString());
        Call<AnalizarImagenResponse> call= service.savePost(req);
        call.enqueue(new Callback<AnalizarImagenResponse>() {
            @Override
            public void onResponse(Call<AnalizarImagenResponse> call, Response<AnalizarImagenResponse> response) {
                //textView.setText(response.toString());
                textView.setText(response.body().getMessage());
                Toast.makeText(MainActivity.this, "Se envío correctamente la petición. Falta retorno del servidor."+ response.toString(), Toast.LENGTH_SHORT).show();
            }

            @Override
            public void onFailure(Call<AnalizarImagenResponse> call, Throwable t) {
                textView.setText(t.getMessage());
            }

        });
        /*
        Call<String> call = service.callTest();
        call.enqueue(new Callback<String>() {
            @Override
            public void onResponse(Call<String> call, Response<String> response) {
                textView.setText(response.toString());
            }

            @Override
            public void onFailure(Call<String> call, Throwable t) {
                textView.setText(t.getMessage());
            }
        });*/

    }

    private String convertImgString(){

        int size = (int) f.length();
        byte[] bytes = new byte[size];
        try {
            BufferedInputStream buf = new BufferedInputStream(new FileInputStream(f));
            buf.read(bytes, 0, bytes.length);
            buf.close();
        } catch (FileNotFoundException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        } catch (IOException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }

        return Base64.encodeToString(bytes,Base64.DEFAULT);
    }

    private void askCameraPermissions() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this, new String[] { Manifest.permission.CAMERA, Manifest.permission.WRITE_EXTERNAL_STORAGE ,Manifest.permission.READ_EXTERNAL_STORAGE}, 0);
        }else{
            dispatchTakePictureIntent();
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        if (requestCode == 0) {
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED
                    && grantResults[1] == PackageManager.PERMISSION_GRANTED) {
                dispatchTakePictureIntent();
            }else {
                Toast.makeText(this,"Se requiere permisos para utilizar la cámara",Toast.LENGTH_SHORT).show();
            }
        }
    }

    private void dispatchTakePictureIntent() {
        Intent takePictureIntent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
        // Ensure that there's a camera activity to handle the intent
        if (takePictureIntent.resolveActivity(getPackageManager()) != null) {
            // Create the File where the photo should go
            File photoFile = null;
            try {
                photoFile = createImageFile();
            } catch (IOException ex) {
                // Error occurred while creating the File

            }
            // Continue only if the File was successfully created
            if (photoFile != null) {
                Uri photoURI = FileProvider.getUriForFile(this,
                        "com.example.skinnerapp.fileprovider",
                        photoFile);
                takePictureIntent.putExtra(MediaStore.EXTRA_OUTPUT, photoURI);
                startActivityForResult(takePictureIntent, REQUEST_TAKE_PHOTO);
            }
        }
    }

    @SuppressLint("MissingSuperCall")
    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
       //super.onActivityResult(requestCode, resultCode, data);

       if(requestCode == REQUEST_TAKE_PHOTO){
           if(resultCode == Activity.RESULT_OK){
               f =new File(currentPhotoPath);
               imageView.setImageURI(Uri.fromFile(f));
               Intent mediaScanIntent = new Intent(Intent.ACTION_MEDIA_SCANNER_SCAN_FILE);
               Uri contentUri = Uri.fromFile(f);
               mediaScanIntent.setData(contentUri);
               this.sendBroadcast(mediaScanIntent);
               btnAnalizar.setVisibility(View.VISIBLE);
           }
       }
    }

    private File createImageFile() throws IOException {
        // Create an image file name
        String timeStamp = new SimpleDateFormat("yyyyMMdd_HHmmss").format(new Date());
        String imageFileName = "JPEG_" + timeStamp + "_";
        File storageDir = getExternalFilesDir(Environment.DIRECTORY_PICTURES);
        //File storageDir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_PICTURES);
        File image = File.createTempFile(
                imageFileName,  /* prefix */
                ".jpg",         /* suffix */
                storageDir      /* directory */
        );

        // Save a file: path for use with ACTION_VIEW intents
        currentPhotoPath = image.getAbsolutePath();
        return image;
    }

}