class EyeController {
  constructor(elements = {}, eyeSize = "33.33vmin") {
    this._eyeSize = eyeSize;
    this._blinkTimeoutID = null;

    this.setElements(elements);
  }

  get leftEye() {
    return this._leftEye;
  }
  get rightEye() {
    return this._rightEye;
  }

  setElements({
    leftEye,
    rightEye,
    upperLeftEyelid,
    upperRightEyelid,
    lowerLeftEyelid,
    lowerRightEyelid,
  } = {}) {
    this._leftEye = leftEye;
    this._rightEye = rightEye;
    this._upperLeftEyelid = upperLeftEyelid;
    this._upperRightEyelid = upperRightEyelid;
    this._lowerLeftEyelid = lowerLeftEyelid;
    this._lowerRightEyelid = lowerRightEyelid;
    return this;
  }

  async blink({ duration = 150 } = {}) {
    console.log("Blinking...");

    // Send API request
    try {
      await fetch("/api/blink", { method: "POST" });
    } catch (error) {
      console.error("API Error:", error);
    }

    if (!this._leftEye) {
      console.warn("Eye elements are not set.");
      return;
    }

    [this._leftEye, this._rightEye].forEach((eye) => {
      eye.animate(
        [
          { transform: "rotateX(0deg)" },
          { transform: "rotateX(90deg)" },
          { transform: "rotateX(0deg)" },
        ],
        {
          duration,
          iterations: 1,
        }
      );
    });
  }

  async express({ type = "", duration = 1000, enterDuration = 75, exitDuration = 75 }) {
    console.log(`Expressing: ${type}`);

    // Send API request
    try {
      await fetch("/api/express", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ type }),
      });
    } catch (error) {
      console.error("API Error:", error);
    }

    if (!this._leftEye) {
      console.warn("Eye elements are not set.");
      return;
    }

    const options = { duration: duration };

    switch (type) {
      case "happy":
        this._lowerLeftEyelid.animate(this._createKeyframes("-2/3", "30deg", enterDuration, exitDuration), options);
        this._lowerRightEyelid.animate(this._createKeyframes("-2/3", "-30deg", enterDuration, exitDuration), options);
        break;
      case "sad":
        this._upperLeftEyelid.animate(this._createKeyframes("1/3", "-20deg", enterDuration, exitDuration), options);
        this._upperRightEyelid.animate(this._createKeyframes("1/3", "20deg", enterDuration, exitDuration), options);
        break;
      case "angry":
        this._upperLeftEyelid.animate(this._createKeyframes("1/4", "30deg", enterDuration, exitDuration), options);
        this._upperRightEyelid.animate(this._createKeyframes("1/4", "-30deg", enterDuration, exitDuration), options);
        break;
      case "focused":
        this._upperLeftEyelid.animate(this._createKeyframes("1/3", "0deg", enterDuration, exitDuration), options);
        this._upperRightEyelid.animate(this._createKeyframes("1/3", "0deg", enterDuration, exitDuration), options);
        this._lowerLeftEyelid.animate(this._createKeyframes("-1/3", "0deg", enterDuration, exitDuration), options);
        this._lowerRightEyelid.animate(this._createKeyframes("-1/3", "0deg", enterDuration, exitDuration), options);
        break;
      case "confused":
        this._upperRightEyelid.animate(this._createKeyframes("1/3", "-10deg", enterDuration, exitDuration), options);
        break;
      default:
        console.warn(`Invalid expression type: ${type}`);
    }
  }

  _createKeyframes(tgtTranYVal, tgtRotVal, enterDuration, exitDuration) {
    return [
      { transform: "translateY(0px) rotate(0deg)", offset: 0.0 },
      { transform: `translateY(calc(${this._eyeSize} * ${tgtTranYVal})) rotate(${tgtRotVal})`, offset: enterDuration / 1000 },
      { transform: `translateY(calc(${this._eyeSize} * ${tgtTranYVal})) rotate(${tgtRotVal})`, offset: 1 - exitDuration / 1000 },
      { transform: "translateY(0px) rotate(0deg)", offset: 1.0 },
    ];
  }

  startBlinking({ maxInterval = 5000 } = {}) {
    if (this._blinkTimeoutID) {
      console.warn(`Already blinking with timeoutID=${this._blinkTimeoutID}; return;`);
      return;
    }

    const blinkRandomly = (timeout) => {
      this._blinkTimeoutID = setTimeout(() => {
        this.blink();
        blinkRandomly(Math.random() * maxInterval);
      }, timeout);
    };
    blinkRandomly(Math.random() * maxInterval);
  }

  stopBlinking() {
    clearTimeout(this._blinkTimeoutID);
    this._blinkTimeoutID = null;
  }
}

const eyes = new EyeController({
  leftEye: document.querySelector(".left.eye"),
  rightEye: document.querySelector(".right.eye"),
  upperLeftEyelid: document.querySelector(".left .eyelid.upper"),
  upperRightEyelid: document.querySelector(".right .eyelid.upper"),
  lowerLeftEyelid: document.querySelector(".left .eyelid.lower"),
  lowerRightEyelid: document.querySelector(".right .eyelid.lower"),
});

// Button Event Listeners
document.querySelector("button:nth-child(1)").addEventListener("click", () => eyes.startBlinking());
document.querySelector("button:nth-child(2)").addEventListener("click", () => eyes.stopBlinking());
document.querySelector("button:nth-child(3)").addEventListener("click", () => eyes.blink());
document.querySelector("button:nth-child(4)").addEventListener("click", () => eyes.express({ type: "happy" }));
document.querySelector("button:nth-child(5)").addEventListener("click", () => eyes.express({ type: "sad" }));
document.querySelector("button:nth-child(6)").addEventListener("click", () => eyes.express({ type: "angry" }));
document.querySelector("button:nth-child(7)").addEventListener("click", () => eyes.express({ type: "focused" }));
document.querySelector("button:nth-child(8)").addEventListener("click", () => eyes.express({ type: "confused" }));

const socket = new WebSocket("ws://localhost:8765");

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    if (data.emotion) {
        eyes.express({ type: data.emotion });
    }
};

socket.onopen = function() {
    console.log("WebSocket connected.");
};

socket.onclose = function() {
    console.log("WebSocket closed.");
};

socket.onerror = function(error) {
    console.error("WebSocket Error:", error);
};