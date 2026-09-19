import sys, cv2, numpy as np
# usage: align.py ref.png moving.png out.png  -> warps moving onto ref geometry (similarity transform)
ref = cv2.imread(sys.argv[1]); mov = cv2.imread(sys.argv[2])
g1 = cv2.cvtColor(ref, cv2.COLOR_BGR2GRAY); g2 = cv2.cvtColor(mov, cv2.COLOR_BGR2GRAY)
orb = cv2.ORB_create(8000)
k1, d1 = orb.detectAndCompute(g1, None); k2, d2 = orb.detectAndCompute(g2, None)
m = sorted(cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True).match(d2, d1), key=lambda x: x.distance)[:1500]
src = np.float32([k2[x.queryIdx].pt for x in m]); dst = np.float32([k1[x.trainIdx].pt for x in m])
M, inl = cv2.estimateAffinePartial2D(src, dst, method=cv2.RANSAC, ransacReprojThreshold=4)
s = np.hypot(M[0,0], M[1,0]); print("scale %.3f tx %.1f ty %.1f inliers %d/%d" % (s, M[0,2], M[1,2], inl.sum(), len(m)))
bg = tuple(int(v) for v in np.median(mov[5:40, -200:-5].reshape(-1,3), axis=0))
out = cv2.warpAffine(mov, M, (ref.shape[1], ref.shape[0]), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_CONSTANT, borderValue=bg)
cv2.imwrite(sys.argv[3], out)
