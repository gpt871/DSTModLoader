#import <Foundation/Foundation.h>

static void DSTEnsureModsDirectory(void)
{
    @autoreleasepool {
        NSArray<NSString *> *paths =
            NSSearchPathForDirectoriesInDomains(NSDocumentDirectory,
                                                 NSUserDomainMask,
                                                 YES);
        if (paths.count == 0) {
            return;
        }

        NSString *documents = paths.firstObject;
        NSString *gameRoot =
            [documents stringByAppendingPathComponent:@"DoNotStarveTogether"];
        NSString *mods =
            [gameRoot stringByAppendingPathComponent:@"mods"];

        NSFileManager *fm = [NSFileManager defaultManager];
        NSError *error = nil;

        if (![fm createDirectoryAtPath:mods
           withIntermediateDirectories:YES
                            attributes:nil
                                 error:&error]) {
            NSLog(@"[DSTModLoader] failed to create mods directory: %@", error);
            return;
        }

        NSLog(@"[DSTModLoader] mods directory: %@", mods);
    }
}

__attribute__((constructor))
static void DSTModLoaderInit(void)
{
    DSTEnsureModsDirectory();
}

