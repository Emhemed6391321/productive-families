import React from 'react';
import {Composition} from 'remotion';
import {WalkingMontage, WALKING_MONTAGE_DURATION} from './WalkingMontage';

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="WalkingMontage"
      component={WalkingMontage}
      durationInFrames={WALKING_MONTAGE_DURATION}
      fps={30}
      width={1080}
      height={1920}
    />
  );
};
