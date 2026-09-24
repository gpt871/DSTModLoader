#!/usr/bin/env python3
import struct, sys, shutil

LC_LOAD_DYLIB = 0xC
MH_MAGIC_64 = 0xfeedfacf

def align8(x): return (x + 7) & ~7

def patch(src, dst, dylib="@executable_path/Frameworks/DSTModLoader.dylib"):
    b = bytearray(open(src, "rb").read())
    magic, = struct.unpack_from("<I", b, 0)
    if magic != MH_MAGIC_64:
        raise SystemExit("not a 64-bit little-endian Mach-O")

    # mach_header_64: magic,cputype,cpusubtype,filetype,ncmds,sizeofcmds,flags,reserved
    ncmds, sizeofcmds = struct.unpack_from("<II", b, 16)

    # Existing load commands start immediately after the 32-byte header.
    cmds_end = 32 + sizeofcmds

    # Find first section file offset from LC_SEGMENT_64 commands.
    off = 32
    first_section_offset = None
    for _ in range(ncmds):
        cmd, cmdsize = struct.unpack_from("<II", b, off)
        if cmdsize < 8 or off + cmdsize > len(b):
            raise SystemExit("invalid load command")
        if cmd == 0x19:  # LC_SEGMENT_64
            # segment_command_64: cmd,cmdsize,segname[16],vmaddr,vmsize,fileoff,filesize,...
            nsects = struct.unpack_from("<I", b, off + 64)[0]
            sectoff = off + 72
            for i in range(nsects):
                so = sectoff + i * 80
                if so + 80 <= len(b):
                    fileoff = struct.unpack_from("<Q", b, so + 48)[0]
                    if fileoff and (first_section_offset is None or fileoff < first_section_offset):
                        first_section_offset = fileoff
        off += cmdsize

    if first_section_offset is None:
        raise SystemExit("could not find a section")

    name = dylib.encode() + b"\\x00"
    cmdsize = align8(24 + len(name))
    new_end = cmds_end + cmdsize
    if new_end > first_section_offset:
        raise SystemExit("not enough room for an additional load command")

    # Avoid duplicate insertion.
    off = 32
    for _ in range(ncmds):
        cmd, oldsize = struct.unpack_from("<II", b, off)
        if cmd in (LC_LOAD_DYLIB, 0x18):  # load dylib / weak dylib
            nameoff = struct.unpack_from("<I", b, off + 8)[0]
            end = off + oldsize
            raw = bytes(b[off + nameoff:end]).split(b"\\x00",1)[0]
            if raw.decode(errors="ignore") == dylib:
                shutil.copy2(src, dst)
                print("already present; copied unchanged")
                return
        off += oldsize

    # Append command into the free area between load commands and first section.
    payload = bytearray(cmdsize)
    struct.pack_into("<II", payload, 0, LC_LOAD_DYLIB, cmdsize)
    struct.pack_into("<IIII", payload, 8, 24, 0, 0, 0)  # name, timestamp, current, compat
    payload[24:24+len(name)] = name

    b[cmds_end:new_end] = payload
    struct.pack_into("<I", b, 16, ncmds + 1)
    struct.pack_into("<I", b, 20, sizeofcmds + cmdsize)

    open(dst, "wb").write(b)
    print(f"patched: {dst}")
    print(f"load command: {dylib}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: patch_load_dylib.py ORIGINAL OUTPUT")
        raise SystemExit(2)
    patch(sys.argv[1], sys.argv[2])
