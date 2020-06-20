package com.example.skinnerapp;

import androidx.appcompat.app.AppCompatActivity;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.view.animation.Animation;
import android.view.animation.AnimationUtils;
import android.widget.Button;
import android.widget.ImageView;

public class BodyActivity extends AppCompatActivity {

    private Button button_frente;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_body);

        button_frente = (Button) findViewById(R.id.button_frente);

        button_frente.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {

                Intent resultIntent = new Intent();
                resultIntent.putExtra("bodyPart","frente");  // put data that you want returned to activity A
                setResult(Activity.RESULT_OK, resultIntent);
                finish();
            }
        });

    }
}