import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--model", type=str, default="./model/RWKV-4-Raven-7B-v9x-Eng49%-Chn50%-Other1%-20230418-ctx4096-cudaf16i8")
parser.add_argument("--strategy", type=str, default="cuda fp16i8")
parser.add_argument("--cuda_on", type=str, default="1", help="RWKV_CUDA_ON value")
parser.add_argument("--jit_on", type=str, default="1", help="RWKV_JIT_ON value")
cmd_opts = parser.parse_args()

from rwkv.model import RWKV

model_path = f"{cmd_opts.model}"

RWKV(model=model_path, strategy=cmd_opts.strategy,
     convert_and_save_and_exit=f"{cmd_opts.model[0:-4]}-{cmd_opts.strategy}.pth")
