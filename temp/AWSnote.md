### Key-Pair

    * Unique
    * Can be save as .pem file

### Security group


### Placement group

    * A placement group is a logical grouping of instances within a single Availability Zone.
    * Using placement groups enables applications to participate in a low-latency, 10 Gbps network.

    * A placement group can''t span multiple Availability Zones.
    * The following are the only instance types that you can use when you launch an instance into a placement group:

        * Compute optimized: c4.large | c4.xlarge | c4.2xlarge | c4.4xlarge | c4.8xlarge | c3.large | c3.xlarge | c3.2xlarge | c3.4xlarge | c3.8xlarge | cc2.8xlarge

        * GPU: cg1.4xlarge | g2.2xlarge | g2.8xlarge

        * Memory optimized: cr1.8xlarge | r3.large | r3.xlarge | r3.2xlarge | r3.4xlarge | r3.8xlarge

        * Storage optimized: d2.xlarge | d2.2xlarge | d2.4xlarge | d2.8xlarge | hi1.4xlarge | hs1.8xlarge | i2.xlarge | i2.2xlarge | i2.4xlarge | i2.8xlarge
    * Only some of the instance types can take full advantage of the network speeds.


### VPC

    Amazon Virtual Private Cloud (Amazon VPC) enables you to launch Amazon Web Services (AWS) resources into a virtual network that you''ve defined. This virtual network closely resembles a traditional network that you''d operate in your own data center, with the benefits of using the scalable infrastructure of AWS.


### Benefits of Using a VPC

By launching your instances into a VPC instead of EC2-Classic, you gain the ability to:

    * Assign static private IP addresses to your instances that persist across starts and stops

    * Assign multiple IP addresses to your instances

    * Define network interfaces, and attach one or more network interfaces to your instances

    * Change security group membership for your instances while they''re running

    * Control the outbound traffic from your instances (egress filtering) in addition to controlling the inbound traffic to them (ingress filtering)

    * Add an additional layer of access control to your instances in the form of network access control lists (ACL)

    * Run your instances on single-tenant hardware


