TARGET := iphone:clang:latest:15.0
ARCHS := arm64

include $(THEOS)/makefiles/common.mk

TWEAK_NAME := DSTModLoader

DSTModLoader_FILES := src/Tweak.xm
DSTModLoader_FRAMEWORKS := Foundation UIKit
DSTModLoader_CFLAGS := -fobjc-arc -Wno-deprecated-declarations

DSTModLoader_INSTALL_TARGET_PROCESSES := dontstarvetogether

include $(THEOS_MAKE_PATH)/tweak.mk
