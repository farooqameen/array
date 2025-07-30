import React from "react";

/**
 * Array Logo
 */
const WaveLogo = ({ width = 100, height = 100 }) => (
  <svg
    id="Layer_1"
    data-name="Layer 1"
    xmlns="http://www.w3.org/2000/svg"
    version="1.1"
    xmlnsXlink="http://www.w3.org/1999/xlink"
    viewBox="0 0 1000 1000"
    width={width}
    height={height}
  >
    <defs>
      <style>
        {`
          .cls-1 {
            fill: var(--array-text-color, #ff18f3);
          }
          .cls-1, .cls-2, .cls-3, .cls-4 {
            stroke-width: 0px;
          }
          .cls-2 {
            fill: var(--logo-color, url(#Wave_form_3-2));
          }
          .cls-3 {
            fill: var(--logo-color, url(#Wave_form_3));
          }
          .cls-4 {
            fill: var(--logo-color, url(#Wave_form_3-3));
          }
        `}
      </style>
      <linearGradient
        id="Wave_form_3"
        data-name="Wave form 3"
        x1="1029.07"
        y1="1263.3"
        x2="1877.4"
        y2="1263.3"
        gradientTransform="translate(2266.76 -14.83) rotate(123.74)"
        gradientUnits="userSpaceOnUse"
      >
        <stop offset="0" stopColor="#2302ff" />
        <stop offset=".04" stopColor="#2a02fe" />
        <stop offset=".11" stopColor="#3e04fc" />
        <stop offset=".19" stopColor="#5e07f9" />
        <stop offset=".27" stopColor="#8c0cf5" />
        <stop offset=".37" stopColor="#c512f0" />
        <stop offset=".45" stopColor="#ff18eb" />
        <stop offset=".47" stopColor="#f51ee8" />
        <stop offset=".58" stopColor="#b64ad8" />
        <stop offset=".68" stopColor="#826fcb" />
        <stop offset=".78" stopColor="#598cc0" />
        <stop offset=".87" stopColor="#3ca0b9" />
        <stop offset=".94" stopColor="#2aadb4" />
        <stop offset="1" stopColor="#24b2b3" />
      </linearGradient>
      <linearGradient
        id="Wave_form_3-2"
        data-name="Wave form 3"
        x1="1293.77"
        y1="1047.83"
        x2="1892.94"
        y2="1047.83"
        xlinkHref="#Wave_form_3"
      />
      <linearGradient
        id="Wave_form_3-3"
        data-name="Wave form 3"
        x1="742.91"
        y1="230.54"
        x2="975.75"
        y2="230.54"
        gradientTransform="translate(-134.02 416.94) rotate(-19.29)"
        xlinkHref="#Wave_form_3"
      />
    </defs>
    <g>
      <path
        className="cls-3"
        d="M13.31,737.77L489.7,35.8l176.09,418.79L13.31,737.77ZM483.74,95.88L92.95,671.71l535.23-232.29L483.74,95.88Z"
      />
      <path
        className="cls-2"
        d="M25.09,764.33l666.31-275.51,295.1,217.3L25.09,764.33ZM687.42,521.73l-491.67,203.3,709.43-42.96-217.76-160.35Z"
      />
      <path
        className="cls-4"
        d="M986.69,665.38l-284.73-215.22L519.77,36.02l466.92,629.36ZM725.23,431.57l118.67,89.7-194.61-262.3,75.94,172.61Z"
      />
    </g>
    <g>
      <path
        className="cls-1"
        d="M271.81,964.2l-19.23-32.47h-60.7l10.59-18.28h39.35l-28.59-48.26-58.23,99h-25.59l73.76-123.49c2.65-4.43,6-7.27,10.94-7.27s8.12,2.84,10.76,7.27l73.94,123.49h-27Z"
      />
      <path
        className="cls-1"
        d="M431.67,964.2l-32.47-35.84h-48v-19.87h53.47c16.06,0,24.53-9.23,24.53-25.9s-9.17-24.84-24.53-24.84h-69.87v106.46h-22.23v-128.99h92.11c29.29,0,46.58,18.28,46.58,47.02,0,21.29-9.88,36.37-26.47,42.76l38.64,39.21h-31.76Z"
      />
      <path
        className="cls-1"
        d="M594.17,964.2l-32.47-35.84h-48v-19.87h53.47c16.06,0,24.53-9.23,24.53-25.9s-9.17-24.84-24.53-24.84h-69.87v106.46h-22.23v-128.99h92.11c29.29,0,46.58,18.28,46.58,47.02,0,21.29-9.88,36.37-26.47,42.76l38.64,39.21h-31.76Z"
      />
      <path
        className="cls-1"
        d="M771.33,964.2l-19.23-32.47h-60.7l10.59-18.28h39.35l-28.59-48.26-58.23,99h-25.59l73.76-123.49c2.65-4.43,6-7.27,10.94-7.27s8.12,2.84,10.76,7.27l73.94,123.49h-27Z"
      />
      <path
        className="cls-1"
        d="M834.49,964.2v-48.97l-68.11-80.02h30.17l49.94,59.44,50.11-59.44h28.59l-68.29,80.02v48.97h-22.41Z"
      />
    </g>
  </svg>
);

export default WaveLogo;
