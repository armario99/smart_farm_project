package com.example.smart_parm_project;
import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.TextView;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.net.Socket;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;

public class MainActivity extends AppCompatActivity {
    int select_num_temp,select_num_hum,select_num_light,select_num_music = 1;
    int selected = 0;
    int selected_sen = 1;
    boolean check = false;
    Button connect_btn,disconnect_btn;
    Button plus_btn,hum_btn, temp_btn, mus_btn,lig_btn;
    EditText ip_edit;
    TextView show_text;

    String[] parts;

    // about socket
    private Handler mHandler;

    private Socket socket;

    private DataOutputStream outstream;
    private DataInputStream instream;

    private int port = 8080;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        ip_edit = (EditText) findViewById(R.id.editText);
        show_text = (TextView) findViewById(R.id.textView);

        Intent intent = getIntent();
        String editTextValue = intent.getStringExtra("ipValue");
        if (editTextValue != null) {
            ip_edit.setText(editTextValue);
        }
        connect_btn = (Button) findViewById(R.id.button);
        connect_btn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                connect();
            }
        });


        hum_btn = (Button) findViewById(R.id.buttonhumidity);
        hum_btn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                selected = 1;
                selected_sen = 1;
                check = true;
                if (select_num_hum >= 3) {
                    select_num_hum = 1;
                }else{
                    select_num_hum +=1;
                }
            }
        });

        temp_btn = (Button) findViewById(R.id.buttontemperature);
        temp_btn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                selected = 2;
                selected_sen = 2;
                check = true;
                if (select_num_temp >= 3) {
                    select_num_temp = 1;
                }else{
                    select_num_temp +=1;
                }
            }
        });

        mus_btn = (Button) findViewById(R.id.buttonmusic);
        mus_btn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                selected = 3;
                selected_sen = 3;
                check = true;
                if (select_num_music >= 3) {
                    select_num_music = 1;
                }else{
                    select_num_music +=1;
                }
            }
        });

        lig_btn = (Button) findViewById(R.id.buttonlight);
        lig_btn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                selected = 4;
                selected_sen = 4;
                check = true;
                if (select_num_light >= 3) {
                    select_num_light = 1;
                }else{
                    select_num_light +=1;
                }
            }
        });

        disconnect_btn = (Button) findViewById(R.id.dis_button);
        disconnect_btn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                selected = 6;
                selected_sen = 6;
                check = true;


            }
        });
    }

    void connect(){
        mHandler = new Handler(Looper.getMainLooper());
        Log.w("connect","연결 하는중");

        Thread checkUpdate = new Thread(){
            public void run(){
                // Get ip
                String newip = String.valueOf(ip_edit.getText());
                TextView textView = findViewById(R.id.sensortext);
                ImageView imageView = findViewById(R.id.imageView);
                // Access server
                try{
                    socket = new Socket(newip, port);
                    Log.w("서버 접속됨", "서버 접속됨");
                }catch (IOException e1){
                    Log.w("서버 접속 못함", "서버 접속 못함");
                    e1.printStackTrace();
                }

                Log.w("edit 넘어가야 할 값 : ","안드로이드에서 서버로 연결 요청");

                try{
                    outstream = new DataOutputStream(socket.getOutputStream());
                    instream = new DataInputStream(socket.getInputStream());
                    outstream.writeUTF("안드로이드에서 서버로 연결 요청");
                }catch(IOException e){
                    e.printStackTrace();
                    Log.w("버퍼","버퍼 생성 잘못 됨");
                }
                Log.w("버퍼","버퍼 생성 잘 됨");
                //다음 명령어 입력
                try{
                    while(true){
                        String msg = "";
                        if (check == true) {
                            if (selected == 0) {
                                msg = msg ;
                            } else if (selected >= 1 && selected <= 4) {
                                String[][] additionalTexts = {{"습도 auto","습도 On","습도 Off"},
                                                              {"온도 auto","온도 On","온도 Off"},
                                                              {"음악 Off","음악 1","음악 2"},
                                                              {"조도 auto","조도 On","조도 Off"}};
                                String additionalText = "";
                                if (selected == 1){
                                    additionalText = additionalTexts[selected - 1][select_num_hum - 1];
                                    final String finalMsg1 = additionalText;
                                    runOnUiThread(new Runnable() {
                                        @Override
                                        public void run() {
                                            hum_btn.setText(finalMsg1);
                                        }
                                    });
                                } else if (selected == 2) {
                                    additionalText = additionalTexts[selected - 1][select_num_temp - 1];
                                    final String finalMsg2 = additionalText;
                                    runOnUiThread(new Runnable() {
                                        @Override
                                        public void run() {
                                            temp_btn.setText(finalMsg2);
                                        }
                                    });
                                } else if (selected == 3) {
                                    additionalText = additionalTexts[selected - 1][select_num_music - 1];
                                    final String finalMsg3 = additionalText;
                                    runOnUiThread(new Runnable() {
                                        @Override
                                        public void run() {
                                            mus_btn.setText(finalMsg3);
                                        }
                                    });
                                } else if (selected == 4) {
                                    additionalText = additionalTexts[selected - 1][select_num_light - 1];
                                    final String finalMsg4 = additionalText;
                                    runOnUiThread(new Runnable() {
                                        @Override
                                        public void run() {
                                            lig_btn.setText(finalMsg4);
                                        }
                                    });
                                }

                                msg = additionalText;
                            } else if (selected == 6) {
                                msg = "연결 종료";
                                final String endMsg1 = "습도";
                                final String endMsg2 = "온도";
                                final String endMsg3 = "음악";
                                final String endMsg4 = "빛";
                                runOnUiThread(new Runnable() {
                                    @Override
                                    public void run() {
                                        hum_btn.setText(endMsg1);
                                        temp_btn.setText(endMsg2);
                                        mus_btn.setText(endMsg3);
                                        lig_btn.setText(endMsg4);
                                    }
                                });
                            }

                            byte[] data = msg.getBytes();
                            ByteBuffer b1 = ByteBuffer.allocate(4);
                            b1.order(ByteOrder.LITTLE_ENDIAN);
                            b1.putInt(data.length);
                            outstream.write(b1.array(), 0, 4);
                            outstream.write(data);

                            data = new byte[4];
                            instream.read(data, 0, 4);
                            ByteBuffer b2 = ByteBuffer.wrap(data);
                            b2.order(ByteOrder.LITTLE_ENDIAN);
                            int length = b2.getInt();
                            data = new byte[length];
                            instream.read(data, 0, length);

                            msg = new String(data, "UTF-8");
                            show_text.setText(msg);
                            parts = msg.split(" ");

                            try {
                                if (selected_sen == 1) {
                                    double hum_num = Double.parseDouble(parts[4]);
                                    if (hum_num >= 70.00) {
                                        textView.setText("현재 상태 : 습함");

                                  imageView.setImageResource(R.drawable.high_water);
                                    } else if (hum_num >= 50.00 && hum_num < 70.00) {
                                        textView.setText("현재 상태 : 보통");
                                        imageView.setImageResource(R.drawable.middle_water);
                                    } else {
                                        textView.setText("현재 상태 : 건조함");
                                        imageView.setImageResource(R.drawable.low_water);
                                    }
                                } else if (selected_sen == 2) {
                                    double temp_num = Double.parseDouble(parts[1]);
                                    if (temp_num >= 27.00) {
                                        textView.setText("현재 상태 : 더움");
                                        imageView.setImageResource(R.drawable.high_temp);
                                    } else if (temp_num >= 15.00 && temp_num < 27.00) {
                                        textView.setText("현재 상태 : 선선함");
                                        imageView.setImageResource(R.drawable.middle_temp);
                                    } else {
                                        textView.setText("현재 상태 : 추움");
                                        imageView.setImageResource(R.drawable.low_temp);
                                    }
                                } else if (selected_sen == 4) {
                                    int light_num = Integer.parseInt(parts[7]);
                                    if (light_num >= 150) {
                                        textView.setText("현재 상태 : 어두움");
                                        imageView.setImageResource(R.drawable.low_light);
                                    } else {
                                        textView.setText("현재 상태 : 밝음");
                                        imageView.setImageResource(R.drawable.high_light);
                                    }
                                }
                                else if (selected_sen == 6) {
                                    textView.setText("현재 상태 : 미 입력");
                                    imageView.setImageResource(R.drawable.plant);
                                }
                            } catch(Exception e){
                                textView.setText("데이터 동기화 중....");
                                e.printStackTrace();
                            }


                            selected = 7;
                            check = false;
                            data = null;

                            if (selected == 6) {
                                disconnect();
                            }
                        } else {
                            byte[] data = new byte[4];
                            if (instream.available() >= 4) {
                                instream.read(data, 0, 4);
                                ByteBuffer b2 = ByteBuffer.wrap(data);
                                b2.order(ByteOrder.LITTLE_ENDIAN);
                                int length = b2.getInt();
                                data = new byte[length];
                                instream.read(data, 0, length);
                                String msg2 = new String(data, "UTF-8");
                                // UI 업데이트 코드 수정
                                final String finalMsg2 = msg2;
                                runOnUiThread(new Runnable() {
                                    @Override
                                    public void run() {
                                        show_text.setText(finalMsg2);
                                    }
                                });
                            }
                        }
                    }
                }catch(Exception e){
                    String error_msg = e.getMessage(); // 예외 메시지 추출
                    if (error_msg == "Only the original thread that created a view hierarchy can touch its views."){
                        error_msg = "연결이 해제되었습니다.";
                    }
                    e.printStackTrace(); // 예외 정보를 출력
                    final String finalMsg2 = error_msg;
                    runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            show_text.setText(finalMsg2);
                        }
                    });
                    selected = 7;
                    check = false;
                }
            }
        };
        checkUpdate.start();
    }
    void disconnect() {
        try {
            if (socket != null) {
                socket.close();
                Log.w("소켓 연결 종료", "소켓 연결이 성공적으로 종료되었습니다.");
            }
        } catch (IOException e) {
            e.printStackTrace();
            Log.w("소켓 연결 종료 오류", "소켓 연결 종료 중 오류가 발생했습니다.");
        }
    }
}
