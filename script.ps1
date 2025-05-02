
        cd "./piper"
        echo 'SAMPLE.' | ./piper --model BT7274.onnx --output_file ../output/"Pilot, mission is nearing completion".wav --length_scale 1.0 --noise_w 1.0 --noise_scale 0.666
        