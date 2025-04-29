import cairosvg
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        "Convert SVG to PNG for use with ffmpeg")
    parser.add_argument("--algorithm", type=str, default="minimax")
    parser.add_argument("--moves", type=int, default=34)
    args = parser.parse_args()
    for idx in range(args.moves+1):
        cairosvg.svg2png(
            url=f"gameplay_frames/svg/{args.algorithm}_frame_{idx:03d}.svg", write_to=f"gameplay_frames/png/{args.algorithm}_frame_{idx:03d}.png")
