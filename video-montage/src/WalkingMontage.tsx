import React from 'react';
import {
  AbsoluteFill,
  Img,
  Sequence,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';

const SHOT_FRAMES = 90; // 3 seconds per shot at 30fps
const FADE_FRAMES = 10;
const SHOT_COUNT = 4;
export const WALKING_MONTAGE_DURATION = SHOT_FRAMES * SHOT_COUNT;

type Shot = {
  // Camera framing, varied per shot to read as different angles.
  scaleFrom: number;
  scaleTo: number;
  originX: string;
  originY: string;
  translateFromX: number;
  translateToX: number;
  rotateFrom: number;
  rotateTo: number;
};

const SHOTS: Shot[] = [
  // 1. Wide establishing shot, slow push-in.
  {scaleFrom: 1.0, scaleTo: 1.08, originX: '50%', originY: '50%', translateFromX: 0, translateToX: 0, rotateFrom: 0, rotateTo: 0},
  // 2. Close-up on the upper body, drifting upward.
  {scaleFrom: 1.6, scaleTo: 1.8, originX: '45%', originY: '35%', translateFromX: 0, translateToX: 0, rotateFrom: 0, rotateTo: 0},
  // 3. Tracking shot, sliding sideways as if following the walk.
  {scaleFrom: 1.2, scaleTo: 1.2, originX: '50%', originY: '50%', translateFromX: 70, translateToX: -70, rotateFrom: 0, rotateTo: 0},
  // 4. Low-angle hero shot with a slight tilt that settles level.
  {scaleFrom: 1.3, scaleTo: 1.05, originX: '50%', originY: '85%', translateFromX: 0, translateToX: 0, rotateFrom: -2, rotateTo: 0},
];

const Shot: React.FC<{shot: Shot; src: string}> = ({shot, src}) => {
  const frame = useCurrentFrame();
  const {width, height} = useVideoConfig();

  const progress = interpolate(frame, [0, SHOT_FRAMES], [0, 1], {extrapolateRight: 'clamp'});
  const scale = interpolate(progress, [0, 1], [shot.scaleFrom, shot.scaleTo]);
  const translateX = interpolate(progress, [0, 1], [shot.translateFromX, shot.translateToX]);
  const rotate = interpolate(progress, [0, 1], [shot.rotateFrom, shot.rotateTo]);

  // Small vertical bob to suggest the rhythm of walking.
  const bob = Math.sin((frame / 15) * Math.PI * 2) * 6;

  const opacity = interpolate(
    frame,
    [0, FADE_FRAMES, SHOT_FRAMES - FADE_FRAMES, SHOT_FRAMES],
    [0, 1, 1, 0],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
  );

  return (
    <AbsoluteFill style={{opacity}}>
      <Img
        src={src}
        style={{
          width,
          height,
          objectFit: 'cover',
          transformOrigin: `${shot.originX} ${shot.originY}`,
          transform: `translate(${translateX}px, ${bob}px) rotate(${rotate}deg) scale(${scale})`,
        }}
      />
    </AbsoluteFill>
  );
};

export const WalkingMontage: React.FC = () => {
  const src = staticFile('walker.jpg');
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();

  return (
    <AbsoluteFill style={{backgroundColor: '#000', overflow: 'hidden'}}>
      {/* Blurred backdrop fills the 9:16 frame behind the shots. */}
      <AbsoluteFill style={{opacity: 0.6}}>
        <Img
          src={src}
          style={{width: '100%', height: '100%', objectFit: 'cover', filter: 'blur(40px) brightness(0.6)'}}
        />
      </AbsoluteFill>

      {SHOTS.map((shot, index) => (
        <Sequence key={index} from={index * SHOT_FRAMES} durationInFrames={SHOT_FRAMES}>
          <Shot shot={shot} src={src} />
        </Sequence>
      ))}

      {/* Progress bar across the top. */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          height: 6,
          width: `${(frame / durationInFrames) * 100}%`,
          backgroundColor: '#f5f5f5',
        }}
      />
    </AbsoluteFill>
  );
};
