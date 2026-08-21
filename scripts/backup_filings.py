#!/usr/bin/env python3
"""
财报文件备份脚本 — 防止误删双保险

功能：
- 将主目录 data/raw/cn_财报/ 和 us_财报/ 增量备份到 dev 目录
- 只复制新增或修改的文件（基于文件大小和修改时间）
- dev 目录的备份不受主目录删除操作影响（单向同步）

用法：
    python scripts/backup_filings.py          # 执行备份
    python scripts/backup_filings.py --dry-run # 预览模式（不实际复制）
    python scripts/backup_filings.py --verify  # 验证备份完整性
"""

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path


def get_repo_paths():
    """自动定位主目录和 dev 目录。"""
    script_dir = Path(__file__).resolve().parent
    main_repo = script_dir.parent
    # dev 目录可能在主目录内部（子目录），也可能与主目录同级
    dev_repo = main_repo / "depreciation-risk-detection-dev"
    if not dev_repo.exists():
        dev_repo = main_repo.parent / "depreciation-risk-detection-dev"
    
    if not dev_repo.exists():
        # 尝试从当前工作目录推断
        cwd = Path.cwd()
        if cwd.name == "depreciation-risk-detection-dev":
            dev_repo = cwd
            main_repo = cwd.parent / "depreciation-risk-detection"
        elif cwd.name == "depreciation-risk-detection":
            main_repo = cwd
            dev_repo = cwd / "depreciation-risk-detection-dev"
    
    return main_repo, dev_repo
    """自动定位主目录和 dev 目录。"""
    script_dir = Path(__file__).resolve().parent
    main_repo = script_dir.parent
    dev_repo = main_repo.parent / "depreciation-risk-detection-dev"
    
    if not dev_repo.exists():
        # 尝试从当前工作目录推断
        cwd = Path.cwd()
        if cwd.name == "depreciation-risk-detection-dev":
            dev_repo = cwd
            main_repo = cwd.parent / "depreciation-risk-detection"
        elif cwd.name == "depreciation-risk-detection":
            main_repo = cwd
            dev_repo = cwd.parent / "depreciation-risk-detection-dev"
    
    return main_repo, dev_repo


def backup_folder(src: Path, dst: Path, dry_run: bool = False) -> dict:
    """单向增量备份：src → dst。
    
    Returns:
        {"copied": int, "skipped": int, "removed": int, "errors": list}
    """
    stats = {"copied": 0, "skipped": 0, "removed": 0, "errors": []}
    
    if not src.exists():
        stats["errors"].append(f"源目录不存在: {src}")
        return stats
    
    dst.mkdir(parents=True, exist_ok=True)
    
    # 收集源文件
    src_files = {f.relative_to(src): f for f in src.rglob("*") if f.is_file()}
    dst_files = {f.relative_to(dst): f for f in dst.rglob("*") if f.is_file()}
    
    # 复制新增或修改的文件
    for rel_path, src_file in src_files.items():
        dst_file = dst / rel_path
        
        needs_copy = False
        if not dst_file.exists():
            needs_copy = True
            reason = "新增"
        else:
            # 比较大小和修改时间
            src_stat = src_file.stat()
            dst_stat = dst_file.stat()
            if src_stat.st_size != dst_stat.st_size or src_stat.st_mtime > dst_stat.st_mtime:
                needs_copy = True
                reason = "修改"
        
        if needs_copy:
            if dry_run:
                print(f"  [预览] 将复制 ({reason}): {rel_path}")
            else:
                try:
                    dst_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_file, dst_file)
                    print(f"  ✅ 已复制 ({reason}): {rel_path}")
                except Exception as e:
                    stats["errors"].append(f"复制失败 {rel_path}: {e}")
                    print(f"  ❌ 复制失败: {rel_path} — {e}")
                    continue
            stats["copied"] += 1
        else:
            stats["skipped"] += 1
    
    # 注意：不删除 dst 中有但 src 中没有的文件（保护性设计，防止主目录误删导致备份也被删）
    # 如果需要清理，可单独调用 --verify 模式
    
    return stats


def verify_backup(main_repo: Path, dev_repo: Path) -> dict:
    """验证备份完整性，报告主目录和 dev 目录的差异。"""
    results = {}
    
    for folder_name in ["cn_财报", "us_财报"]:
        src = main_repo / "data" / "raw" / folder_name
        dst = dev_repo / "data" / "raw" / folder_name
        
        src_count = sum(1 for _ in src.rglob("*") if _.is_file()) if src.exists() else 0
        dst_count = sum(1 for _ in dst.rglob("*") if _.is_file()) if dst.exists() else 0
        
        missing = []
        if src.exists():
            for f in src.rglob("*"):
                if f.is_file():
                    dst_file = dst / f.relative_to(src)
                    if not dst_file.exists():
                        missing.append(str(f.relative_to(src)))
        
        results[folder_name] = {
            "src_count": src_count,
            "dst_count": dst_count,
            "missing": missing,
            "ok": len(missing) == 0 and src_count == dst_count,
        }
    
    return results


def main():
    parser = argparse.ArgumentParser(description="财报文件防误删备份工具")
    parser.add_argument("--dry-run", action="store_true", help="预览模式，不实际复制")
    parser.add_argument("--verify", action="store_true", help="验证备份完整性")
    args = parser.parse_args()
    
    main_repo, dev_repo = get_repo_paths()
    
    print("=" * 60)
    print(f"📦 财报备份工具 — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print(f"主目录: {main_repo}")
    print(f"Dev 目录 (备份): {dev_repo}")
    print()
    
    if not dev_repo.exists():
        print(f"❌ 错误: dev 目录不存在: {dev_repo}")
        print("   请确保 depreciation-risk-detection-dev 文件夹与主目录同级")
        sys.exit(1)
    
    if args.verify:
        print("🔍 验证备份完整性...")
        results = verify_backup(main_repo, dev_repo)
        all_ok = True
        for folder_name, info in results.items():
            print(f"\n  📁 {folder_name}:")
            print(f"     主目录: {info['src_count']} 份")
            print(f"     备份:   {info['dst_count']} 份")
            if info['missing']:
                print(f"     ⚠️ 缺失 {len(info['missing'])} 份:")
                for m in info['missing'][:5]:
                    print(f"        - {m}")
                if len(info['missing']) > 5:
                    print(f"        ... 还有 {len(info['missing']) - 5} 份")
                all_ok = False
            else:
                print(f"     ✅ 完整")
        
        print()
        if all_ok:
            print("🎉 所有备份完整！")
        else:
            print("⚠️ 备份不完整，建议立即执行备份！")
        return
    
    # 执行备份
    mode_str = "【预览模式】" if args.dry_run else "【实际备份】"
    print(f"🚀 开始备份 {mode_str}")
    print()
    
    total_copied = 0
    total_skipped = 0
    total_errors = []
    
    for folder_name in ["cn_财报", "us_财报"]:
        src = main_repo / "data" / "raw" / folder_name
        dst = dev_repo / "data" / "raw" / folder_name
        
        print(f"📁 备份 {folder_name}...")
        stats = backup_folder(src, dst, dry_run=args.dry_run)
        
        print(f"   已复制: {stats['copied']} 份")
        print(f"   跳过(已一致): {stats['skipped']} 份")
        if stats['errors']:
            print(f"   错误: {len(stats['errors'])} 个")
        print()
        
        total_copied += stats['copied']
        total_skipped += stats['skipped']
        total_errors.extend(stats['errors'])
    
    # 写入备份日志
    if not args.dry_run:
        log_file = dev_repo / "data" / "backup_log.txt"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().isoformat()}] 备份完成: 复制 {total_copied} 份, 跳过 {total_skipped} 份\n")
        print(f"📝 备份日志已写入: {log_file}")
    
    print("=" * 60)
    if args.dry_run:
        print(f"🔍 预览完成。如需执行实际备份，请去掉 --dry-run 参数重新运行。")
    else:
        print(f"✅ 备份完成！共复制 {total_copied} 份文件，跳过 {total_skipped} 份已一致的文件。")
        if total_errors:
            print(f"⚠️ 有 {len(total_errors)} 个错误，请检查上方输出。")
    print("=" * 60)


if __name__ == "__main__":
    main()
