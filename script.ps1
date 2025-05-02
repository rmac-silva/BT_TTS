
        cd "./piper"
        echo 'Objective near your position pilot.' | ./piper --model BT7274.onnx --output_file ../output/"Objective near your position pilot".wav --length_scale 1.0 --noise_w 1.0 --noise_scale 0.666
        