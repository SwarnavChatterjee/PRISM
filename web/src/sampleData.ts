export const SAMPLE_CISCO_CONFIG = `hostname Core-Switch-01
ip domain-name enterprise.local
ip ssh version 2
ip telnet server
no ip http server
aaa new-model
logging host 10.0.0.50
line vty 0 4
 transport input ssh
`;

export const SAMPLE_JUNIPER_CONFIG = `system {
    host-name Edge-Router-01;
    services {
        ssh {
            protocol-version v2;
        }
        telnet;
    }
    syslog {
        host 10.0.0.60 {
            any any;
        }
    }
}
`;

export function createSampleFile(filename = "sample-cisco-core.cfg", content = SAMPLE_CISCO_CONFIG): File {
  const blob = new Blob([content], { type: "text/plain" });
  return new File([blob], filename, { type: "text/plain" });
}
